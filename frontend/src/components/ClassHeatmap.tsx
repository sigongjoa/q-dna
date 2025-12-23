import React, { useEffect, useState } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { ResponsiveHeatMap } from '@nivo/heatmap';
import simulationData from '../data/simulation_results.json';

export default function ClassHeatmap() {
    // In a real app, we would fetch this via useEffect.
    // Here we import the generated JSON directly.

    return (
        <Paper sx={{ height: 800, p: 2, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
                Real-Time Class Mastery Analysis (BKT Model)
            </Typography>
            <Typography variant="caption" display="block" sx={{ mb: 2 }}>
                Generated from simulated student learning trajectories. Red = Identifying Gaps, Green = Mastered.
            </Typography>

            <Box sx={{ height: 700 }}>
                <ResponsiveHeatMap
                    data={simulationData}
                    margin={{ top: 100, right: 60, bottom: 60, left: 80 }}
                    valueFormat=">-.0f"
                    axisTop={{
                        tickSize: 5,
                        tickPadding: 5,
                        tickRotation: -45,
                        legend: '',
                        legendOffset: 46
                    }}
                    axisLeft={{
                        tickSize: 5,
                        tickPadding: 5,
                        tickRotation: 0,
                        legend: 'Student ID',
                        legendPosition: 'middle',
                        legendOffset: -72
                    }}
                    colors={{
                        type: 'diverging',
                        scheme: 'red_yellow_green',
                        divergeAt: 0.5,
                        minValue: 0,
                        maxValue: 100
                    }}
                    emptyColor="#555555"
                    legends={[
                        {
                            anchor: 'top',
                            translateX: 0,
                            translateY: -50,
                            length: 400,
                            thickness: 8,
                            direction: 'row',
                            tickPosition: 'after',
                            tickSize: 3,
                            tickSpacing: 4,
                            tickOverlap: false,
                            tickFormat: '>-.0f',
                            title: 'Mastery Probability (%)',
                            titleAlign: 'start',
                            titleOffset: 4
                        }
                    ]}
                    hoverTarget="cell"
                    cellHoverOthersOpacity={0.25}
                />
            </Box>
        </Paper>
    );
}
