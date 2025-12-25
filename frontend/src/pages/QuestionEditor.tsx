import React, { useState } from 'react';
import { Box, Button, TextField, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Grid, Chip, Stack, CircularProgress, Alert, Divider, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import AutoBenchmarkIcon from '@mui/icons-material/AutoAwesome';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CurriculumTree from '../components/CurriculumTree';

// Types mimicking backend schemas
interface ExamSourceInfo { name: string; year: number; grade: number; number: number; }
interface MathDomainInfo { major_domain: string; advanced_topic: string; }

export default function QuestionEditor() {
    const [questionType, setQuestionType] = useState('mcq');
    const [content, setContent] = useState('');
    const [selectedCurriculumIds, setSelectedCurriculumIds] = useState<number[]>([]);

    // Advanced Metadata State
    const [examSource, setExamSource] = useState<ExamSourceInfo>({ name: '', year: 2024, grade: 5, number: 1 });
    const [mathDomain, setMathDomain] = useState<MathDomainInfo>({ major_domain: '', advanced_topic: '' });
    const [difficulty, setDifficulty] = useState<number>(3);

    // AI Simulation State
    const [isAiProcessing, setIsAiProcessing] = useState(false);
    const [aiTags, setAiTags] = useState<{ name: string, type: string, confidence: number }[]>([]);
    const [aiFeedback, setAiFeedback] = useState<string | null>(null);

    // Twin Generation State
    const [isTwinGenerating, setIsTwinGenerating] = useState(false);
    const [twinResult, setTwinResult] = useState<string | null>(null);

    const handleAiAnalyze = () => {
        setIsAiProcessing(true);
        // Simulate API Call to /api/v1/questions/analyze
        setTimeout(() => {
            setIsAiProcessing(false);
            setAiTags([
                { name: 'Linear Equations', type: 'Concept', confidence: 0.98 },
                { name: 'KMC-Style', type: 'ExamType', confidence: 0.95 },
                { name: 'Critical Thinking', type: 'Skill', confidence: 0.85 },
            ]);
            // Auto-fill metadata based on analysis
            setExamSource(prev => ({ ...prev, name: 'KMC', grade: 5 }));
            setMathDomain({ major_domain: 'Geometry', advanced_topic: 'Congruence' });
            setDifficulty(4);
            setAiFeedback("Identified as a KMC-style geometry problem requiring auxiliary line construction.");
        }, 1500);
    };

    const handleGenerateTwin = () => {
        setIsTwinGenerating(true);
        // Simulate API Call to /api/v1/questions/{id}/twin
        setTimeout(() => {
            setIsTwinGenerating(false);
            setTwinResult(`[Generated Twin Problem]\nA triangle ABC has AB=AC. Point D is on BC such that...\n(Structurally identical to original but with different values)`);
        }, 2000);
    };

    const handleSave = () => {
        const payload = {
            questionType,
            content,
            curriculum: selectedCurriculumIds,
            tags: aiTags,
            metadata: {
                source: examSource,
                domain: mathDomain,
                difficulty: difficulty,
                ai_feedback: aiFeedback
            }
        };
        console.log("Saving Advanced Math Question...", payload);
        alert("Question Saved! (Check Console)");
    };

    return (
        <Paper sx={{ p: 4, maxWidth: 1200, margin: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h5">
                    Question Editor (Advanced Math)
                </Typography>
                <Stack direction="row" spacing={2}>
                    <Button
                        variant="outlined"
                        color="success"
                        startIcon={isTwinGenerating ? <CircularProgress size={20} /> : <ContentCopyIcon />}
                        onClick={handleGenerateTwin}
                        disabled={isTwinGenerating || !content}
                    >
                        Generate Twin
                    </Button>
                    <Button
                        variant="contained"
                        color="secondary"
                        startIcon={isAiProcessing ? <CircularProgress size={20} color="inherit" /> : <AutoBenchmarkIcon />}
                        onClick={handleAiAnalyze}
                        disabled={isAiProcessing || !content}
                    >
                        {isAiProcessing ? "Analyzing..." : "AI Auto-Tag"}
                    </Button>
                </Stack>
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
                            label="Question Stem (Markdown/LaTeX)"
                            multiline
                            rows={12}
                            fullWidth
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Type problem here..."
                        />

                        {aiFeedback && (
                            <Alert severity="info" onClose={() => setAiFeedback(null)}>
                                <strong>AI Insight:</strong> {aiFeedback}
                            </Alert>
                        )}

                        {twinResult && (
                            <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f9fbe7', borderColor: '#c0ca33' }}>
                                <Typography variant="subtitle2" color="success.main" gutterBottom>
                                    Twin Problem Generated:
                                </Typography>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                                    {twinResult}
                                </Typography>
                                <Button size="small" sx={{ mt: 1 }}>Apply to Editor</Button>
                            </Paper>
                        )}
                    </Stack>
                </Grid>

                {/* Right Column: Metadata & Curriculum */}
                <Grid item xs={12} md={5}>
                    <Accordion defaultExpanded sx={{ mb: 2 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="subtitle1">Advanced Metadata</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <Stack spacing={2}>
                                <TextField
                                    label="Exam Source"
                                    size="small"
                                    value={examSource.name}
                                    onChange={(e) => setExamSource({ ...examSource, name: e.target.value })}
                                    placeholder="e.g. KMC, HME"
                                />
                                <Stack direction="row" spacing={2}>
                                    <TextField
                                        label="Year" type="number" size="small"
                                        value={examSource.year}
                                        onChange={(e) => setExamSource({ ...examSource, year: parseInt(e.target.value) })}
                                    />
                                    <TextField
                                        label="Grade" type="number" size="small"
                                        value={examSource.grade}
                                        onChange={(e) => setExamSource({ ...examSource, grade: parseInt(e.target.value) })}
                                    />
                                </Stack>
                                <Divider />
                                <TextField
                                    label="Major Domain"
                                    size="small"
                                    value={mathDomain.major_domain}
                                    onChange={(e) => setMathDomain({ ...mathDomain, major_domain: e.target.value })}
                                />
                                <TextField
                                    label="Advanced Topic"
                                    size="small"
                                    value={mathDomain.advanced_topic}
                                    onChange={(e) => setMathDomain({ ...mathDomain, advanced_topic: e.target.value })}
                                />
                                <FormControl size="small">
                                    <InputLabel>Difficulty (1-5)</InputLabel>
                                    <Select
                                        value={difficulty}
                                        label="Difficulty (1-5)"
                                        onChange={(e) => setDifficulty(Number(e.target.value))}
                                    >
                                        {[1, 2, 3, 4, 5].map(l => <MenuItem key={l} value={l}>Level {l}</MenuItem>)}
                                    </Select>
                                </FormControl>
                            </Stack>
                        </AccordionDetails>
                    </Accordion>

                    <Typography variant="h6" gutterBottom>AI Suggested Tags</Typography>
                    <Paper variant="outlined" sx={{ p: 2, mb: 3, minHeight: 80 }}>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {aiTags.map((tag) => (
                                <Chip
                                    key={tag.name}
                                    label={tag.name}
                                    color={tag.type === 'ExamType' ? "secondary" : "default"}
                                    size="small"
                                />
                            ))}
                        </Box>
                    </Paper>

                    <Box sx={{ height: 250, overflow: 'auto' }}>
                        <CurriculumTree onSelectionChange={setSelectedCurriculumIds} />
                    </Box>
                </Grid>

                <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, pt: 2, borderTop: '1px solid #eee' }}>
                        <Button variant="outlined">Save Draft</Button>
                        <Button variant="contained" onClick={handleSave}>
                            Save Question
                        </Button>
                    </Box>
                </Grid>
            </Grid>
        </Paper>
    );
}
