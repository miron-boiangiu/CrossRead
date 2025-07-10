'use client';

import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import { Box, Button, CircularProgress } from '@mui/material';
import { useState } from 'react';
import { ToastContainer, Bounce, toast } from 'react-toastify';

import { BASE_LINK } from './globals_vars';
import InsertUrlPage from './pages/InsertUrlPage';
import ComparisonPage from './pages/ComparisonPage';
import ArticleSelectPage from './pages/ArticleSelectPage';

export interface AlternativeSource {
  "domain": string,
  "link": string,
  "title": string | null,
  "publish_date": string | null,
  "top_image": string | null,
  "text": string | null,
}

export default function Home() {
  const [link, setLink] = useState('');
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedLink, setSelectedLink] = useState('');
  const [links, setLinks] = useState<AlternativeSource[]>([]);
  const [report, setReport] = useState('');
  const [darkMode, setDarkMode] = useState(true);

  const handleCompare = async () => {
    if (selectedLink) {
      setLoading(true);
      console.log('Comparing link:', selectedLink);

      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          { article_link1: link,
            article_link2: selectedLink
          })
      };

      await fetch(BASE_LINK + '/compute_diff', requestOptions)
      .then(response => response.json())
      .then(data => {
        if ('error' in data) {
          throw new Error(data.error)
        } else {
          setReport(data.output)
          setStep(2);
        }
  
      })
      .catch((error) => {
        console.log(error)
        toast.error(String(error), {
          position: "top-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: false,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
          theme: "colored",
          transition: Bounce,
          });

          setSelectedLink('');
          setLinks([]);
          setReport('');
          setStep(0);
      });

      setLoading(false);
    } else {
      toast.info('Please select a link for comparison.', {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: false,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "colored",
        transition: Bounce,
        });
    }
  };

  const handleSubmit = async () => {

    setLoading(true);
    console.log('Submitted link:', link);

    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_link: link })
    };

    await fetch(BASE_LINK + '/search_similar', requestOptions)
    .then(response => response.json())
    .then(data => {
      if ('error' in data) {
        throw new Error(data.error)
      } else {
        setLinks(data)
        setStep(1);
      }

    })
    .catch((error) => {
      console.log(error)
      toast.error(String(error), {
        position: "top-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: false,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "colored",
        transition: Bounce,
        });
    });

    setLoading(false);
  };

  const handleCompareAnother = async () => {
    console.log('Compare another clicked');
    setSelectedLink('');
    setLinks([]);
    setReport('');
    setStep(0);
  };

  return (
    <>
      <ToastContainer />
      <Box
        sx={{
          minHeight: '100vh',
          bgcolor: darkMode ? 'black' : 'background.paper',
          color: darkMode ? 'white' : 'text.primary',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        {
          loading && <CircularProgress size={64} sx={{ color: darkMode? 'white' : 'black' }} />
        }
        {
          !loading && step===0 && <InsertUrlPage link={link} setLink={setLink} handleSubmit={handleSubmit} darkMode={darkMode}/>
        }
        {
          !loading && step===1 && <ArticleSelectPage selectedLink={selectedLink} setSelectedLink={setSelectedLink} links={links} handleCompare={handleCompare} darkMode={darkMode}/>
        }
        {
          !loading && step===2 && <ComparisonPage comparisonResult={report} handleCompareAnother={handleCompareAnother} darkMode={darkMode}/>
        }
      </Box>
  
      <Button
        variant="contained"
        onClick={() => setDarkMode(!darkMode)}
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 9999,
          bgcolor: darkMode ? 'grey.800' : 'grey.200',
          color: darkMode ? 'white' : 'black',
          minWidth: 0,
          width: 48,
          height: 48,
          borderRadius: '50%',
          '&:hover': {
            bgcolor: darkMode ? 'grey.700' : 'grey.300',
          }
        }}
      >
        {darkMode ? <DarkModeIcon /> : <LightModeIcon />}
      </Button>

    </>
  );
  
}
