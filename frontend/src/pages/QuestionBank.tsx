import { useEffect, useState } from 'react';
import {
    Box, Paper, Typography, Button, Chip, Stack, Alert,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Tooltip, CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import { questionService } from '../services/api';

// Define strict type locally or import if shared
interface Question {
    question_id: string;
    content_stem: string;
    question_type: string;
    content_metadata: any;
    status: string;
    created_at: string;
}

export default function QuestionBank() {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState<Question[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isWorksheetMode, setIsWorksheetMode] = useState(false);

    useEffect(() => {
        loadQuestions();
    }, []);

    const loadQuestions = async () => {
        try {
            setLoading(true);
            const data = await questionService.getAll();
            // Sort by created_at desc
            data.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            setQuestions(data);
        } catch (err) {
            console.error("Failed to load questions", err);
            setError("Failed to load questions. Is backend running?");
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = () => {
        navigate('/questions/new');
    };

    const handleRowClick = (id: string) => {
        navigate(`/questions/${id}`);
    };

    const toggleWorksheetMode = () => {
        setIsWorksheetMode(!isWorksheetMode);
    };

    const handlePrint = () => {
        window.print();
    };

    if (isWorksheetMode) {
        return (
            <Box sx={{ p: 4, bgcolor: 'white', minHeight: '100vh', fontFamily: 'serif' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4, '@media print': { display: 'none' } }}>
                    <Button variant="outlined" onClick={toggleWorksheetMode}>Back to Bank</Button>
                    <Box>
                        <Typography variant="caption" sx={{ mr: 2 }}>Use Browser Print to Save as PDF</Typography>
                        <Button variant="contained" onClick={handlePrint}>Print</Button>
                    </Box>
                </Box>

                <Stack spacing={4} sx={{ maxWidth: '210mm', margin: 'auto' }}>
                    <Box sx={{ borderBottom: '2px solid black', pb: 2, mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                        <Box>
                            <Typography variant="h4" fontWeight="bold">Advanced Math Worksheet</Typography>
                            <Typography variant="subtitle1">Q-DNA Generated</Typography>
                        </Box>
                        <Typography variant="h6" sx={{ minWidth: 200, borderBottom: '1px solid black' }}>Name: </Typography>
                    </Box>

                    {questions.map((q, index) => (
                        <Box key={q.question_id} sx={{ breakInside: 'avoid', mb: 4, pageBreakInside: 'avoid' }}>
                            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                                <Typography variant="h6" fontWeight="bold" sx={{ minWidth: 30 }}>{index + 1}.</Typography>
                                <Typography variant="h6" sx={{ lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{q.content_stem}</Typography>
                            </Box>
                            {/* Space for working */}
                            <Box sx={{ height: '150px' }} />
                        </Box>
                    ))}
                </Stack>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
                <Typography variant="h5" component="h1" fontWeight="bold" sx={{ color: 'primary.main' }}>
                    Question Bank
                </Typography>
                <Stack direction="row" spacing={2}>
                    <Button
                        variant="outlined"
                        color="secondary"
                        onClick={toggleWorksheetMode}
                    >
                        Worksheet Mode
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleCreate}
                    >
                        Create New
                    </Button>
                </Stack>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <TableContainer component={Paper} elevation={2} sx={{ borderRadius: 2 }}>
                <Table sx={{ minWidth: 650 }} aria-label="question table">
                    <TableHead sx={{ bgcolor: 'grey.50' }}>
                        <TableRow>
                            <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Domain / Difficulty</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Content Preview</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Source</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                                    <CircularProgress size={24} /> Loading...
                                </TableCell>
                            </TableRow>
                        ) : questions.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                                    No questions found. Create one!
                                </TableCell>
                            </TableRow>
                        ) : (
                            questions.map((q) => {
                                const meta = q.content_metadata || {};
                                const domain = meta.domain?.major_domain || 'Uncategorized';
                                const level = meta.difficulty?.estimated_level || '?';
                                const source = meta.source?.name || '-';
                                const isTwin = meta.is_twin_generated;

                                return (
                                    <TableRow
                                        key={q.question_id}
                                        hover
                                        sx={{ cursor: 'pointer', '&:last-child td, &:last-child th': { border: 0 } }}
                                        onClick={() => handleRowClick(q.question_id)}
                                    >
                                        <TableCell>
                                            <Chip
                                                label={isTwin ? "Twin" : q.status}
                                                color={isTwin ? "success" : (q.status === 'published' ? "primary" : "default")}
                                                size="small"
                                                sx={{ fontWeight: 'bold' }}
                                                variant={isTwin ? "filled" : "outlined"}
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Stack direction="row" spacing={1} alignItems="center">
                                                <Typography variant="body2" fontWeight="medium" color="text.secondary">{domain}</Typography>
                                                <Chip label={`Lv.${level}`} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                                            </Stack>
                                        </TableCell>
                                        <TableCell sx={{ maxWidth: 400 }}>
                                            <Typography noWrap variant="body2" color="text.primary">
                                                {q.content_stem}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="caption" display="block">{source}</Typography>
                                            <Typography variant="caption" color="text.secondary">{meta.source?.year}</Typography>
                                        </TableCell>
                                        <TableCell align="right">
                                            <Tooltip title="View/Edit">
                                                <IconButton size="small" onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/questions/${q.question_id}`);
                                                }}>
                                                    <EditIcon fontSize="small" color="action" />
                                                </IconButton>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                );
                            })
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
}
