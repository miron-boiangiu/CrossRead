'use client';

import { Box, Button, Container, Typography, Paper } from '@mui/material';

interface ComparisonPageParams {
  comparisonResult: string;
  handleCompareAnother: any;
  darkMode: boolean;
}

export default function ComparisonPage({
  comparisonResult,
  handleCompareAnother,
  darkMode
}: ComparisonPageParams) {
  return (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" alignItems="center" gap={4}>
        <Typography variant="h4" align="center">
          Comparison Result
        </Typography>

        <Typography variant="body1" align="center" sx={{ color: darkMode?'#ccc':'#555', mb: 2 }}>
          The two articles you have selected have been analyzed and a report has been generated! Here is the result of the comparison:
        </Typography>

        <Paper
          elevation={3}
          sx={{
            backgroundColor: darkMode? '#1a1a1a':'#f5f5f5',
            color: darkMode? 'white':'black',
            padding: 3,
            whiteSpace: 'pre-wrap',
            width: '100%',
            textAlign: 'left',
            fontFamily: 'monospace',
            maxHeight: '50vh',
            overflowY: 'auto',
            paddingRight: 1, // optional, for scrollbar padding
          }}
        >
          {comparisonResult}
        </Paper>

        <Button
          variant="contained"
          onClick={handleCompareAnother}
          sx={{
            bgcolor: '#1976d2',
            ':hover': { bgcolor: '#1565c0' },
            color: '#fff',
            width: '200px',
          }}
        >
          Compare Another
        </Button>
      </Box>
    </Container>
  );
}
