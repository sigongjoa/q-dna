
import { Grid, Paper, Typography } from '@mui/material';

export default function DashboardPage() {
    return (
        <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 4 }}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                        Total Questions
                    </Typography>
                    <Typography component="p" variant="h3">
                        1,250
                    </Typography>
                </Paper>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                        Pending Review
                    </Typography>
                    <Typography component="p" variant="h3">
                        45
                    </Typography>
                </Paper>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
                <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
                    <Typography component="h2" variant="h6" color="primary" gutterBottom>
                        Quality Alerts
                    </Typography>
                    <Typography component="p" variant="h3" color="error">
                        3
                    </Typography>
                </Paper>
            </Grid>
        </Grid>
    );
}
