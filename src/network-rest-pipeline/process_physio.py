"""Process physio data from Flywheel and create a summary CSV."""

import csv
from collections import defaultdict
from pathlib import Path

import flywheel
from flywheel import ApiException

from utils.flywheel_utils import find_physio_files
from utils.subject_utils import get_valid_subjects, normalize_subject_id
from config import FLYWHEEL_PROJECT, OUTPUT_DIR

def process_physio_data(output_csv: str = f'{OUTPUT_DIR}/physio_summary.csv') -> None:
    """Process physio data from Flywheel and create summary CSV."""
    print(f'Connecting to Flywheel project: {FLYWHEEL_PROJECT}')

    try:
        fw = flywheel.Client()
    except ValueError as e:
        print(f'Error: {e}')
        return

    try:
        project = fw.lookup(FLYWHEEL_PROJECT)
        if not project:
            print(f'Error: Project "{FLYWHEEL_PROJECT}" not found')
            return

        print(f'Found project: {project.label}\n')

        # Get valid subjects (in both validation and discovery files)
        valid_subjects = get_valid_subjects()

        # Collect all subjects and their sessions
        # subject_id -> list of (session_id, session_label, has_physio, timestamp)
        # timestamp can be datetime.datetime or None
        subject_sessions: dict[str, list[tuple[str, str, bool, object]]] = (
            defaultdict(list)
        )

        all_subjects = project.subjects()
        print(f'Total subjects in project: {len(all_subjects)}')

        for subject in all_subjects:
            normalized_id = normalize_subject_id(subject.code)

            # Only process subjects that are in both validation and discovery files
            if normalized_id not in valid_subjects:
                continue

            # Get all sessions for this subject
            # subject.sessions is a Finder object - call it to get the list
            try:
                sessions = subject.sessions()
            except (TypeError, AttributeError):
                # Fallback: use client method
                try:
                    sessions = fw.get_subject_sessions(subject.id)
                except Exception:
                    print(f'Warning: Could not get sessions for subject {subject.code}')
                    continue

            for session in sessions:
                session_id = session.id
                session_label = session.label
                # Get timestamp for sorting (could be datetime or None)
                session_timestamp = getattr(session, 'timestamp', None)

                # Check analyses in this session
                # session.analyses might be a list or a Finder object
                has_physio = False
                try:
                    if isinstance(session.analyses, list):
                        analyses = session.analyses
                    elif callable(session.analyses):
                        analyses = session.analyses()
                    else:
                        analyses = list(session.analyses)
                    
                    # Debug: print number of analyses found
                    num_analyses = len(analyses) if hasattr(analyses, '__len__') else 0
                    if num_analyses > 0:
                        print(f'  Found {num_analyses} analyses for session {session_label}')
                    
                    for analysis in analyses:
                        # Reload analysis to ensure files are loaded
                        try:
                            # Try to reload the analysis with files
                            if hasattr(analysis, 'id'):
                                analysis = fw.get_analysis(analysis.id)
                        except (ApiException, AttributeError, TypeError):
                            pass  # Continue with existing analysis object
                        
                        if find_physio_files(analysis):
                            has_physio = True
                            analysis_label = getattr(analysis, 'label', getattr(analysis, 'id', 'unknown'))
                            print(f'  ✓ Found physio files in analysis {analysis_label}')
                            break
                except (ApiException, AttributeError, TypeError) as e:
                    print(
                        f'Warning: Could not get analyses for session {session_label}: {e}'
                    )

                subject_sessions[normalized_id].append(
                    (session_id, session_label, has_physio, session_timestamp)
                )

        # Sort sessions by timestamp to determine chronological order
        # Then renumber them as ses-01, ses-02, etc.
        output_data = []
        for subject_id in sorted(subject_sessions.keys()):
            sessions = subject_sessions[subject_id]

            # Sort sessions by timestamp (earliest first)
            # Handle datetime objects and None values
            def sort_key(session_tuple):
                timestamp = session_tuple[3]
                if timestamp is None:
                    return (float('inf'), session_tuple[1])  # No timestamp, sort by label
                # datetime objects are directly comparable
                return (timestamp, session_tuple[1])
            
            sessions_sorted = sorted(sessions, key=sort_key)

            for idx, (session_id, original_label, has_physio, _) in enumerate(
                sessions_sorted, start=1
            ):
                new_session_label = f'ses-{idx:02d}'
                output_data.append(
                    {
                        'subject_id': subject_id,
                        'session': new_session_label,
                        'has_physio': has_physio,
                        'original_session_label': original_label,
                    }
                )

        # Write to CSV
        output_path = Path(output_csv)
        with output_path.open('w', newline='') as f:
            if output_data:
                fieldnames = ['subject_id', 'session', 'has_physio']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in output_data:
                    writer.writerow(
                        {
                            'subject_id': row['subject_id'],
                            'session': row['session'],
                            'has_physio': row['has_physio'],
                        }
                    )

        print(f'\nSummary written to: {output_csv}')
        print(f'Total subjects: {len(subject_sessions)}')
        print(f'Total sessions: {len(output_data)}')
        sessions_with_physio = sum(1 for row in output_data if row['has_physio'])
        print(f'Sessions with physio: {sessions_with_physio}')

    except ApiException as e:
        print(f'Flywheel API error: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')
        raise


if __name__ == '__main__':
    import sys

    output_file = sys.argv[1] if len(sys.argv) > 1 else f'{OUTPUT_DIR}/physio_summary.csv'
    process_physio_data(output_file)

