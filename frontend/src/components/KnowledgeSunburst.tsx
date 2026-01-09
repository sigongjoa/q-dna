
import { ResponsiveSunburst } from '@nivo/sunburst';
import { Box, Typography, Paper } from '@mui/material';

// Mock Data structure compatible with Nivo Sunburst
const data = {
    name: "Math",
    color: "hsl(25, 70%, 50%)",
    children: [
        {
            name: "Algebra",
            color: "hsl(148, 70%, 50%)",
            children: [
                { name: "Linear", color: "hsl(253, 70%, 50%)", loc: 70 },
                { name: "Quadratics", color: "hsl(66, 70%, 50%)", loc: 45 },
                { name: "Polynomials", color: "hsl(25, 70%, 50%)", loc: 30 }
            ]
        },
        {
            name: "Geometry",
            color: "hsl(297, 70%, 50%)",
            children: [
                { name: "Triangles", color: "hsl(206, 70%, 50%)", loc: 90 },
                { name: "Circles", color: "hsl(315, 70%, 50%)", loc: 60 }
            ]
        },
        {
            name: "Calculus",
            color: "hsl(14, 70%, 50%)",
            children: [
                { name: "Limits", color: "hsl(238, 70%, 50%)", loc: 20 },
                { name: "Derivs", color: "hsl(32, 70%, 50%)", loc: 15 }
            ]
        }
    ]
};

export default function KnowledgeSunburst() {
    return (
        <Paper sx={{ height: 500, p: 2 }}>
            <Typography variant="h6" gutterBottom>Knowledge Map (Mastery)</Typography>
            <Box sx={{ height: 450 }}>
                <ResponsiveSunburst
                    data={data}
                    margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                    id="name"
                    value="loc"
                    cornerRadius={2}
                    borderColor={{ theme: 'background' }}
                    colors={{ scheme: 'nivo' }}
                    childColor={{
                        from: 'color',
                        modifiers: [['brighter', 0.1]]
                    }}
                    enableArcLabels={true}
                    arcLabelsSkipAngle={10}
                    arcLabelsTextColor={{
                        from: 'color',
                        modifiers: [['darker', 1.4]]
                    }}
                />
            </Box>
        </Paper>
    );
}
