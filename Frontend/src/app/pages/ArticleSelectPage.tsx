import {
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    CardHeader,
    CardMedia,
    Collapse,
    Container,
    IconButton,
    Radio,
    Typography,
    Avatar,
  } from '@mui/material';
  import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
  import { red } from '@mui/material/colors';
  import { useState } from 'react';
  import { AlternativeSource } from '../page';
  
  interface ArticleSelectPageParams {
    selectedLink: string;
    setSelectedLink: any;
    links: AlternativeSource[];
    handleCompare: any;
    darkMode: boolean;
  }
  
  export default function ArticleSelectPage({
    selectedLink,
    setSelectedLink,
    links,
    handleCompare,
    darkMode
  }: ArticleSelectPageParams) {
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  
    const handleExpandClick = (index: number) => {
      setExpandedIndex(prev => (prev === index ? null : index));
    };
  
    return (
      <Container maxWidth="md" sx={{
        mt:3,
        mb:3,
      }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={4}>
          <Typography variant="h4" align="center">
            Select a Link to Compare
          </Typography>

          <Typography variant="body1" align="center" sx={{ color: darkMode? '#ccc' :'#555', mb: 2 }}>
            The following articles match the topic of the one you gave us! Please, select an alternative source for comparison.
          </Typography>
  
          {/* Cards in 2-column layout */}
          
          <Box
            display="flex"
            flexWrap="wrap"
            alignItems="flex-start"
            gap={1}
            justifyContent="center"
            width="100%"
            sx={{
              maxHeight: "65vh",    // or whatever height you want
              overflowY: 'auto',
              paddingRight: 1,   // optional, for scrollbar padding
            }}
          >

            {links.map((link, index) => (
                <Card
                key={index}
                sx={{
                    width: 'calc(40% - 1rem)', // Fixed width
                    backgroundColor: darkMode? '#1e1e1e' :'#f9f9f9',
                    color: darkMode? 'white' : 'black',
                    display: 'flex',
                    flexDirection: 'column',
                }}
                >
                <CardHeader
                  avatar={
                    <Radio
                      checked={selectedLink === link.link}
                      onChange={() => setSelectedLink(link.link)}
                      value={link.link}
                    />
                  }
                  title={link.title || 'No title available'}
                  subheader={link.publish_date || 'No date'}
                  subheaderTypographyProps={{ color: 'gray' }}
                />
                {(
                  <CardMedia
                    component="img"
                    height="160"
                    image={link.top_image === "" ? '/default_image.webp' : link.top_image ?? '/default_image.webp'}
                    alt={link.title || 'Top image'}
                  />
                )}
                <CardContent>
                  <Typography variant="body2" sx={{ color: darkMode ? 'gray' : '#777' }}>
                    {link.domain}
                  </Typography>
                </CardContent>
                {link.text && (
                  <>
                    <CardActions disableSpacing>
                      <IconButton
                        onClick={() => handleExpandClick(index)}
                        aria-expanded={expandedIndex === index}
                        aria-label="show more"
                        sx={{ color: darkMode? 'white' :'black' }}
                      >
                        <ExpandMoreIcon />
                      </IconButton>
                      <Typography variant="body2" sx={{ color: darkMode ? 'white': 'black' }}>
                        {expandedIndex === index ? 'Hide excerpt' : 'Article excerpt'}
                      </Typography>
                    </CardActions>
                    <Collapse in={expandedIndex === index} timeout="auto" unmountOnExit>
                      <CardContent>
                        <Typography variant="body2" sx={{ color: darkMode ? 'white' : 'black'}}>
                          {link.text}
                        </Typography>
                      </CardContent>
                    </Collapse>
                  </>
                )}
              </Card>
            ))}

        {links.length % 2 === 1 && (
            <Card
              key="placeholder"
              sx={{
                width: 'calc(40% - 1rem)',
                visibility: 'hidden',
                pointerEvents: 'none',
                backgroundColor: 'transparent',
                boxShadow: 'none',
                height: 'auto',
              }}
            />
          )}
          </Box>
          
  
          <Button
            variant="contained"
            onClick={handleCompare}
            sx={{
              bgcolor: '#1976d2',
              ':hover': { bgcolor: '#1565c0' },
              color: '#fff',
              width: '200px',
            }}
          >
            Compare
          </Button>
        </Box>
      </Container>
    );
  }
  