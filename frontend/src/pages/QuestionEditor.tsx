import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Button, TextField, Paper, Typography, FormControl, InputLabel, Select, MenuItem, Grid, Chip, Stack, CircularProgress, Alert, Divider, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import AutoBenchmarkIcon from '@mui/icons-material/AutoAwesome';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import BugReportIcon from '@mui/icons-material/BugReport';
import BrushIcon from '@mui/icons-material/Brush';
import CurriculumTree from '../components/CurriculumTree';
import { questionService, diagramService } from '../services/api';

// Types mimicking backend schemas
interface ExamSourceInfo { name: string; year: number; grade: number; number: number; }
interface MathDomainInfo { major_domain: string; advanced_topic: string; }

export default function QuestionEditor() {
    const { id } = useParams();

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
    const [currentQuestionId, setCurrentQuestionId] = useState<string | null>(null);

    // Diagram Generation State
    const [isDiagramGenerating, setIsDiagramGenerating] = useState(false);
    const [diagramUrl, setDiagramUrl] = useState<string | null>(null);

    // Error Clinic State
    // No specific state needed here, we just navigate

    // Load Data if ID exists
    useEffect(() => {
        if (id) {
            loadQuestion(id);
        }
    }, [id]);

    const loadQuestion = async (qId: string) => {
        try {
            const data = await questionService.getById(qId);
            setCurrentQuestionId(data.question_id);
            setContent(data.content_stem);
            setQuestionType(data.question_type);

            if (data.content_metadata) {
                const meta = data.content_metadata;
                if (meta.source) setExamSource(meta.source);
                if (meta.domain) setMathDomain(meta.domain);
                if (meta.difficulty) setDifficulty(meta.difficulty.estimated_level || 3);
            }
        } catch (error) {
            console.error("Failed to load question:", error);
            alert("Failed to load question data.");
        }
    };

    const handleAiAnalyze = async () => {
        if (!content) return;
        setIsAiProcessing(true);
        try {
            const metadata = await questionService.analyze(content);
            if (metadata.source) setExamSource(prev => ({ ...prev, ...metadata.source }));
            if (metadata.domain) setMathDomain(metadata.domain);
            if (metadata.difficulty) {
                setDifficulty(metadata.difficulty.estimated_level || 3);
                if (metadata.difficulty.required_skills) {
                    setAiTags(metadata.difficulty.required_skills.map((skill: string) => ({
                        name: skill, type: 'Skill', confidence: 0.9
                    })));
                }
            }
            setAiFeedback(`Analyzed as ${metadata.domain?.major_domain} / ${metadata.domain?.advanced_topic}.`);
        } catch (error) {
            console.error("AI Analysis Failed:", error);
            setAiFeedback("Failed to analyze question. Is Ollama running?");
        } finally {
            setIsAiProcessing(false);
        }
    };

    const handleGenerateTwin = async () => {
        if (!currentQuestionId) {
            alert("Please save the question first to generate a twin.");
            return;
        }
        setIsTwinGenerating(true);
        try {
            const twinQuestion = await questionService.createTwin(currentQuestionId);
            setTwinResult(twinQuestion.content_stem);
        } catch (error) {
            console.error("Twin Gen Failed:", error);
            alert("Failed to generate twin problem.");
        } finally {
            setIsTwinGenerating(false);
        }
    };

    const handleGenerateDiagram = async () => {
        if (!content) return;
        setIsDiagramGenerating(true);
        try {
            const result = await diagramService.generate(content);
            const fullUrl = `http://localhost:8000${result.image_url}`;
            setDiagramUrl(fullUrl);
        } catch (error) {
            console.error("Diagram Gen Failed:", error);
            alert("Failed to generate diagram.");
        } finally {
            setIsDiagramGenerating(false);
        }
    };

    const handleNavigateToClinic = () => {
        if (!currentQuestionId) return;
        // Navigate to the Misconception Clinic page
        window.location.href = `/misconception/${currentQuestionId}`;
    };

    // Removed toggleErrorType as dialog is gone

    const handleSave = async () => {
        console.log("Curriculum IDs:", selectedCurriculumIds);
        const payload = {
            question_type: questionType,
            content_stem: content,
            content_metadata: {
                source: examSource,
                domain: mathDomain,
                difficulty: { estimated_level: difficulty },
                ai_feedback: aiFeedback
            },
            answer_key: { "answer": "" },
            create_by: "00000000-0000-0000-0000-000000000000",
            status: "published"
        };

        try {
            const savedQ = await questionService.create(payload);
            setCurrentQuestionId(savedQ.question_id);
            alert("Question Saved! Now you can generate a twin.");
        } catch (error) {
            console.error("Save Failed:", error);
            alert("Failed to save question.");
        }
    };

    return (
        <Paper sx={{ p: 4, maxWidth: 1200, margin: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h5">
                    Question Editor (Advanced Math)
                </Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                        <Button
                            variant="outlined"
                            color="primary"
                            startIcon={isDiagramGenerating ? <CircularProgress size={20} /> : <BrushIcon />}
                            onClick={handleGenerateDiagram}
                            disabled={isDiagramGenerating || !content}
                        >
                            {isDiagramGenerating ? "AI Drawing..." : "Draw Diagram"}
                        </Button>
                        {isDiagramGenerating && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                                Generating... (approx 5-10s)
                            </Typography>
                        )}
                    </Box>
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
                        color="warning"
                        startIcon={<BugReportIcon />}
                        onClick={handleNavigateToClinic}
                        disabled={!currentQuestionId}
                    >
                        Misconcep. Clinic
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
                <Grid size={{ xs: 12, md: 7 }}>
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
                            rows={8}
                            fullWidth
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            placeholder="Type problem here..."
                        />

                        {/* Diagram Preview Area */}
                        {diagramUrl && (
                            <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', bgcolor: '#fafafa' }}>
                                <Typography variant="caption" display="block" color="text.secondary" gutterBottom>Generated Diagram</Typography>
                                <img src={diagramUrl} alt="Generated Geometry" style={{ maxWidth: '100%', maxHeight: 300 }} />
                            </Paper>
                        )}

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

                <Grid size={{ xs: 12, md: 5 }}>
                    {/* Metadata Panel (Simplified for brevity) */}
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

                <Grid size={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, pt: 2, borderTop: '1px solid #eee' }}>
                        <Button variant="outlined">Save Draft</Button>
                        <Button variant="contained" onClick={handleSave}>
                            Save Question
                        </Button>
                    </Box>
                </Grid>
            </Grid>

            {/* Error Dialog Removed */}
        </Paper>
    );
}
