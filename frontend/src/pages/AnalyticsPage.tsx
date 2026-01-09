
import { Grid, Typography, Box } from '@mui/material';
import KnowledgeSunburst from '../components/KnowledgeSunburst';
import ClassHeatmap from '../components/ClassHeatmap';

export default function AnalyticsPage() {
    return (
        <Box>
            <Typography variant="h4" gutterBottom>Analytics Dashboard</Typography>
            <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                    <KnowledgeSunburst />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                    <ClassHeatmap />
                </Grid>
            </Grid>
        </Box>
    );
}
