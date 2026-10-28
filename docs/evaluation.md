# Usage Evaluation

## Efficiency Test Design

### Task 1: Find a Specific Conclusion in Papers
**Manual Method**:
1. Open paper PDF or notes
2. Search for keywords (Ctrl+F)
3. Read through results
4. Verify conclusion context
5. Estimated time: 5-15 minutes per paper

**LabTrail Method**:
1. Open Search page
2. Enter natural language question
3. View ranked results with source references
4. Click to view original document
5. Estimated time: 30 seconds - 2 minutes

### Task 2: Compare Algorithm Performance
**Manual Method**:
1. Open experiment CSV files
2. Filter by method and dataset
3. Calculate statistics manually
4. Create comparison charts in Excel/Python
5. Estimated time: 30-60 minutes

**LabTrail Method**:
1. Open Experiments page
2. View pre-computed comparisons
3. Interactive charts update automatically
4. Export if needed
5. Estimated time: 1-2 minutes

### Task 3: Write Research Weekly Report
**Manual Method**:
1. Review all notes from the week
2. Summarize experiment results
3. List conclusions and decisions
4. Format report
5. Estimated time: 1-2 hours

**LabTrail Method**:
1. Open Reports page
2. Click "Generate Report"
3. Review and export Markdown
4. Estimated time: 1-2 minutes

## Performance Metrics

### System Performance
- Search latency: < 2 seconds (including embedding computation)
- Report generation: < 1 second (template mode)
- Document upload: < 5 seconds per document (including chunking and indexing)
- Frontend load time: < 1 second

### Data Scale (Demo)
- Documents: 8 research notes
- Document chunks: 8 (one per note)
- Experiment records: 30
- Research memories: 6
- Vector dimension: 384

## Evaluation Template

**Note**: The following metrics are to be filled with real user test data.

| Metric | Value | Notes |
|--------|-------|-------|
| Task 1 time (manual) | _ min | To be tested |
| Task 1 time (LabTrail) | _ min | To be tested |
| Task 2 time (manual) | _ min | To be tested |
| Task 2 time (LabTrail) | _ min | To be tested |
| Task 3 time (manual) | _ min | To be tested |
| Task 3 time (LabTrail) | _ min | To be tested |
| User satisfaction | _ / 5 | To be tested |
| Search accuracy | _ % | To be tested |

## Real User Testing

**Status**: Pending

To conduct real user testing:
1. Invite 3-5 researchers to use LabTrail
2. Have them complete the three tasks above
3. Record time taken and satisfaction rating
4. Compare with manual method baseline
5. Collect qualitative feedback

## Usage Statistics

**Status**: To be collected after deployment

Planned metrics to track (with user consent):
- Number of searches performed
- Number of documents uploaded
- Number of reports generated
- Number of memories saved
- Average session duration
- Feature usage frequency
