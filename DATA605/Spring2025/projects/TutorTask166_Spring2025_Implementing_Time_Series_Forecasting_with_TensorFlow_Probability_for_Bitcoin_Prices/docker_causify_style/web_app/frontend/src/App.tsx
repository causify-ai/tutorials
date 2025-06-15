import React, { useEffect, useState, useCallback } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import { format } from 'date-fns';
import { Box, Container, Paper, Typography, Grid, Alert } from '@mui/material';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

interface PriceData {
  timestamp: string;
  close: number;
  prediction?: {
    predicted_price: number;
    upper_bound: number;
    lower_bound: number;
  };
}

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000;

const App: React.FC = () => {
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [latestPrice, setLatestPrice] = useState<number>(0);
  const [latestPrediction, setLatestPrediction] = useState<number | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const connectWebSocket = useCallback(() => {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      setError('Maximum reconnection attempts reached. Please refresh the page.');
      return;
    }

    setConnectionStatus('connecting');
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
      setConnectionStatus('connected');
      setError(null);
      setReconnectAttempts(0);
      console.log('WebSocket connected');
    };
    
    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('WebSocket disconnected');
      
      // Attempt to reconnect
      setTimeout(() => {
        setReconnectAttempts(prev => prev + 1);
        connectWebSocket();
      }, RECONNECT_DELAY);
    };
    
    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('Connection error. Attempting to reconnect...');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setPriceData(prev => [...prev, data].slice(-100)); // Keep last 100 points
        setLatestPrice(data.close);
        if (data.prediction) {
          setLatestPrediction(data.prediction.predicted_price);
        }
      } catch (e) {
        console.error('Error parsing message:', e);
      }
    };

    return ws;
  }, [reconnectAttempts]);

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connectWebSocket]);

  const chartData = {
    labels: priceData.map(d => format(new Date(d.timestamp), 'HH:mm:ss')),
    datasets: [
      {
        label: 'Actual Price',
        data: priceData.map(d => d.close),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        fill: false,
      },
      {
        label: 'Predicted Price',
        data: priceData.map(d => d.prediction?.predicted_price),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        fill: false,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    animation: false,
    scales: {
      x: {
        type: 'time' as const,
        time: {
          unit: 'second'
        },
        title: {
          display: true,
          text: 'Time'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Price (USD)'
        }
      }
    },
    plugins: {
      title: {
        display: true,
        text: 'Bitcoin Price and Predictions'
      }
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Bitcoin Price Dashboard
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Latest Price</Typography>
              <Typography variant="h4" color="primary">
                ${latestPrice.toLocaleString()}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Latest Prediction</Typography>
              <Typography variant="h4" color="secondary">
                {latestPrediction ? `$${latestPrediction.toLocaleString()}` : 'No prediction available'}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ height: 400 }}>
                <Line data={chartData} options={chartOptions} />
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, textAlign: 'right' }}>
          <Typography variant="body2" color={connectionStatus === 'connected' ? 'success.main' : 'error.main'}>
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default App; 