import React, { useState } from 'react';
import { Box, Button, TextField, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Grid, Chip, Stack, CircularProgress, Alert } from '@mui/material';
import AutoBenchmarkIcon from '@mui/icons-material/AutoAwesome';
import CurriculumTree from '../components/CurriculumTree';

export default function QuestionEditor() {
    const [questionType, setQuestionType] = useState('mcq');
    const [content, setContent] = useState('');
    const [selectedCurriculumIds, setSelectedCurriculumIds] = useState<number[]>([]);

    // AI Simulation State
    const [isAiProcessing, setIsAiProcessing] = useState(false);
    const [aiTags, setAiTags] = useState<{ name: string, type: string, confidence: number }[]>([]);
    const [aiFeedback, setAiFeedback] = useState<string | null>(null);

    const handleAiAnalyze = () => {
        setIsAiProcessing(true);
        // Simulate API Call to tagging_service.py
        setTimeout(() => {
            setIsAiProcessing(false);
            setAiTags([
                { name: 'Linear Equations', type: 'Concept', confidence: 0.98 },
                { name: 'Algebra', type: 'Subject', confidence: 0.99 },
                { name: 'Apply', type: 'Cognitive', confidence: 0.85 },
            ]);
            setAiFeedback("This question appears to target analytical skills in basic algebra.");
        }, 2000);
    };

    const handleSave = () => {
        const payload = {
            questionType,
            content,
            curriculum: selectedCurriculumIds,
            tags: aiTags,
            metadata: { ai_feedback: aiFeedback }
        };
        console.log("Saving complex question object...", payload);
    };

    return (
        <Paper sx={{ p: 4, maxWidth: 1200, margin: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h5">
                    Question Editor (Advanced)
                </Typography>
                <Button
                    variant="contained"
                    color="secondary"
                    startIcon={isAiProcessing ? <CircularProgress size={20} color="inherit" /> : <AutoBenchmarkIcon />}
                    onClick={handleAiAnalyze}
                    disabled={isAiProcessing || !content}
                >
                    {isAiProcessing ? "AI analyzing..." : "AI Auto-Tag & Review"}
                </Button>
            </Box>

            <Grid container spacing={4}>
                {/* Left Column: Content */}
                <Grid item xs={12} md={7}>
                    <Stack spacing={3}>
                        <FormControl fullWidth>
                            <InputLabel>Type</InputLabel>
                            <Select
                                value={questionType}
                                label="Type"
                                onChange={(e) => setQuestionType(e.target.value)}
                            >
                                <MenuItem value="mcq">Multiple Choice</MenuItem>
                                <MenuItem value="short_answer">Short Answer</MenuItem>
                                <MenuItem value="essay">Essay / Free Text</MenuItem>
                            </Select>
                        </FormControl>

                        <TextField
                            label="Question Stem (Markdown/LaTeX supported)"
                            multiline
                            rows={12}
                            fullWidth
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Type your question here... use $x^2$ for math."
                            helperText="Supports MathJax/KaTeX rendering"
                        />

                        {aiFeedback && (
                            <Alert severity="info" sx={{ mt: 2 }}>
                                <strong>AI Insight:</strong> {aiFeedback}
                            </Alert>
                        )}
                    </Stack>
                </Grid>

                {/* Right Column: Metadata & Curriculum */}
                <Grid item xs={12} md={5}>
                    <Typography variant="h6" gutterBottom>Curriculum Mapping</Typography>
                    <Typography variant="caption" color="textSecondary" paragraph>
                        Select relevant nodes from the national curriculum tree.
                    </Typography>

                    <Box sx={{ height: 300, overflow: 'auto', mb: 3 }}>
                        <CurriculumTree onSelectionChange={setSelectedCurriculumIds} />
                    </Box>

                    <Typography variant="h6" gutterBottom>AI Suggested Tags</Typography>
                    <Paper variant="outlined" sx={{ p: 2, minHeight: 100 }}>
                        {aiTags.length === 0 ? (
                            <Typography variant="body2" color="textSecondary">
                                Run AI Analysis to generate tags automatically.
                            </Typography>
                        ) : (
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {aiTags.map((tag) => (
                                    <Chip
                                        key={tag.name}
                                        label={`${tag.name} (${Math.round(tag.confidence * 100)}%)`}
                                        color={tag.confidence > 0.9 ? "primary" : "default"}
                                        onDelete={() => { }}
                                    />
                                ))}
                            </Box>
                        )}
                    </Paper>
                </Grid>

                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4, pt: 2, borderTop: '1px solid #eee' }}>
                        <Button variant="outlined">Save as Draft</Button>
                        <Button variant="contained" onClick={handleSave} disabled={selectedCurriculumIds.length === 0}>
                            Save & Publish
                        </Button>
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
}
