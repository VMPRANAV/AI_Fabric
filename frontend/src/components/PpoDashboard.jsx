import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, Typography, LinearProgress, Table, TableBody, TableCell, TableHead, TableRow, Box } from "@mui/material";

// Premium styling: glassmorphism background, smooth gradient, Inter font
const glassStyle = {
  backdropFilter: "blur(12px)",
  background: "rgba(255, 255, 255, 0.15)",
  borderRadius: "12px",
  border: "1px solid rgba(255, 255, 255, 0.3)",
  padding: "24px",
  color: "#fff",
  fontFamily: "'Inter', sans-serif",
};

export default function PpoDashboard() {
  const [status, setStatus] = useState("idle");
  const [timesteps, setTimesteps] = useState(0);
  const [policy, setPolicy] = useState("rule_based");
  const [latest, setLatest] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState(0);

  // Fetch PPO status from backend
  const fetchStatus = async () => {
    try {
      const resp = await axios.get("/api/v1/ppo/status"); // endpoint to be implemented later
      const data = resp.data;
      setPolicy(data.policy);
      setTimesteps(data.timesteps);
      setLatest(data.latest);
      setStatus(data.status);
      setTrainingProgress(data.progress || 0);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Box sx={glassStyle} component={Card} elevation={0}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          PPO Research Dashboard
        </Typography>
        <Typography variant="subtitle1" gutterBottom>
          Policy: {policy} | Timesteps: {timesteps}
        </Typography>
        <Box sx={{ my: 2 }}>
          <Typography variant="body2">Training Status: {status}</Typography>
          {status === "training" && <LinearProgress variant="determinate" value={trainingProgress} />}
        </Box>
        {latest && (
          <Table size="small" sx={{ background: "rgba(255,255,255,0.2)", borderRadius: "8px" }}>
            <TableHead>
              <TableRow>
                <TableCell>Metric</TableCell>
                <TableCell align="right">Value</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>Action</TableCell>
                <TableCell align="right">{latest.action}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Profile</TableCell>
                <TableCell align="right">{latest.profile}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Model</TableCell>
                <TableCell align="right">{latest.model}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Reward</TableCell>
                <TableCell align="right">{latest.reward?.toFixed(3)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Quality</TableCell>
                <TableCell align="right">{latest.quality?.toFixed(3)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Latency (ms)</TableCell>
                <TableCell align="right">{latest.latency_ms?.toFixed(1)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Cost</TableCell>
                <TableCell align="right">{latest.cost?.toFixed(3)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Tool Success</TableCell>
                <TableCell align="right">{latest.tool_success ? "Yes" : "No"}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Box>
  );
}
