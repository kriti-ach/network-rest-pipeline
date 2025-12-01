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

        # Get valid subjects
        valid_subjects = get_valid_subjects()
        subject_sessions: dict[str, list[tuple[str, str, bool, object]]] = (
            defaultdict(list)
        )

        all_subjects = project.subjects()

        for subject in all_subjects:
            normalized_id = normalize_subject_id(subject.code)

            if normalized_id not in valid_subjects:
                continue

            # Reload subject to get full data
            subject = fw.get(subject.id)
            
            # Get sessions - use reload to ensure we have full session data
            sessions = fw.get_subject_sessions(subject.id)

            for session in sessions:
                # Reload the session to get full data including analyses
                session = fw.get(session.id)
                
                session_id = session.id
                session_label = session.label
                print(f"Checking session: {session_label} ({session_id})")
                session_timestamp = getattr(session, 'timestamp', None)

                has_physio = False

                # Get analyses for this session
                analyses = fw.get_session_analyses(session_id)
                
                if analyses:
                    print(f"  Found {len(analyses)} analyses")
                    
                    for analysis in analyses:
                        # Reload analysis to get files
                        analysis = fw.get_analysis(analysis.id)
                        analysis_label = analysis.label
                        
                        print(f"  Checking analysis: {analysis_label}")
                        
                        # Check output files
                        if hasattr(analysis, 'files') and analysis.files:
                            print(f"    Found {len(analysis.files)} output files")
                            for file in analysis.files:
                                print(f"      - {file.name} (type: {file.type})")
                                
                                # Check if it's a physio-related CSV
                                if file.name.endswith('.csv'):
                                    # You can download and read the CSV if needed:
                                    # csv_content = fw.download_file_from_analysis(analysis.id, file.name)
                                    
                                    # Or check the filename pattern
                                    if 'FitData' in file.name or 'FitTrig' in file.name:
                                        has_physio = True
                                        print(f'    ✓ Found physio CSV: {file.name}')
                                        break
                        
                        if has_physio:
                            break
                else:
                    print(f"  No analyses found for session {session_label}")

                subject_sessions[normalized_id].append(
                    (session_id, session_label, has_physio, session_timestamp)
                )
                print(f"  Session summary: Has Physio = {has_physio}\n")

        # [Rest of your code for sorting and writing CSV remains the same]
        output_data = []
        for subject_id in sorted(subject_sessions.keys()):
            sessions = subject_sessions[subject_id]

            def sort_key(session_tuple):
                timestamp = session_tuple[3]
                if timestamp is None:
                    return (float('inf'), session_tuple[1])
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

