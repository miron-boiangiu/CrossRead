'use client';

import { Box, Button, Container, TextField, Typography } from '@mui/material';

interface InsertUrlPageParams {
  link: string;
  setLink: any;
  handleSubmit: any;
  darkMode: boolean;
}

export default function InsertUrlPage({ link, setLink, handleSubmit, darkMode }: InsertUrlPageParams) {
  return (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
        {/* Welcome Title */}
        <Typography variant="h3" align="center">
          Welcome to CrossRead!
        </Typography>

        <Typography variant="body1" align="center" sx={{ color: darkMode? '#ccc' : '#555', mb: 2 }}>
          CrossRead is a platform whose purpose is to compare news articles. Please, start by pasting the URL of the article you wish to analyze!
        </Typography>

        <TextField
          fullWidth
          label="Paste your link here"
          variant="outlined"
          value={link}
          onChange={(e) => setLink(e.target.value)}
          InputLabelProps={{ style: { color: darkMode? '#aaa' :'#555' } }}
          InputProps={{
            style: {
              backgroundColor: darkMode? '#1a1a1a'  : '#f9f9f9',
              color: darkMode? '#fff':'#000',
            },
          }}
          
        />

        <Button
          variant="contained"
          onClick={handleSubmit}
          sx={{
            bgcolor: '#1976d2',
            ':hover': { bgcolor: '#1565c0' },
            color: '#fff',
            width: '200px',
          }}
        >
          Submit
        </Button>
      </Box>
    </Container>
  );
}
