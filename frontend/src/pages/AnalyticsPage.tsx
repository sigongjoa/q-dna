import React from 'react';
import { Grid, Typography, Box } from '@mui/material';
import KnowledgeSunburst from '../components/KnowledgeSunburst';
import ClassHeatmap from '../components/ClassHeatmap';

export default function AnalyticsPage() {
    return (
        <Box>
            <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <KnowledgeSunburst />
                </Grid>
                <Grid item xs={12} md={6}>
                    <ClassHeatmap />
                </Grid>
            </Grid>
        </Box>
    );
}
