import React, { useEffect, useState } from 'react';
import {
    Box, Paper, Typography, Button, Chip, Stack, Alert,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Tooltip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import ContentCopyIcon from '@mui/icons-material/ContentCopy'; // For Twin
import VisibilityIcon from '@mui/icons-material/Visibility';
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

    return (
        <Box sx={{ p: 4, maxWidth: 1200, margin: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
                <Typography variant="h5" component="h1">
                    Question Bank
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreate}
                >
                    Create New
                </Button>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="question table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Status</TableCell>
                            <TableCell>Domain / Difficulty</TableCell>
                            <TableCell>Content Preview</TableCell>
                            <TableCell>Source</TableCell>
                            <TableCell align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={5} align="center">Loading...</TableCell>
                            </TableRow>
                        ) : questions.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} align="center">No questions found. Create one!</TableCell>
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
                                        sx={{ cursor: 'pointer' }}
                                        onClick={() => handleRowClick(q.question_id)}
                                    >
                                        <TableCell>
                                            <Chip
                                                label={isTwin ? "Twin" : q.status}
                                                color={isTwin ? "success" : (q.status === 'published' ? "primary" : "default")}
                                                size="small"
                                                variant="outlined"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Stack direction="row" spacing={1} alignItems="center">
                                                <Typography variant="body2" fontWeight="bold">{domain}</Typography>
                                                <Chip label={`Lv.${level}`} size="small" style={{ height: 20 }} />
                                            </Stack>
                                        </TableCell>
                                        <TableCell sx={{ maxWidth: 400 }}>
                                            <Typography noWrap variant="body2">
                                                {q.content_stem}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>{source} {meta.source?.year}</TableCell>
                                        <TableCell align="right">
                                            <Tooltip title="View/Edit">
                                                <IconButton size="small" onClick={(e) => {
                                                    e.stopPropagation();
                                                    navigate(`/questions/${q.question_id}`);
                                                }}>
                                                    <EditIcon fontSize="small" />
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
