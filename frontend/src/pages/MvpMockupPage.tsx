import React, { useState, useEffect } from 'react';
import {
    Box, Container, Typography, Tabs, Tab, Paper, Button,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    TextField, Checkbox, IconButton, Grid, Chip, Card, CardContent,
    Alert, CircularProgress
} from '@mui/material';
import { cmsService, reportService, analyticsService } from '../services/api';
import DeleteIcon from '@mui/icons-material/Delete';
import DownloadIcon from '@mui/icons-material/Download';
import SendIcon from '@mui/icons-material/Send';
import { ResponsiveSunburst } from '@nivo/sunburst';

// --- Tab Panel Component ---
interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}
function TabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;
    return (
        <div role="tabpanel" hidden={value !== index} {...other}>
            {value === index && (
                <Box sx={{ p: 3 }}>{children}</Box>
            )}
        </div>
    );
}

// --- 1. Bulk Input Panel Mockup ---
const BulkInputMockup = () => {
    // Default valid UUIDs for testing (assuming these don't exist in DB, but format valid)
    const [rows, setRows] = useState([
        { id: 1, student: '00000000-0000-0000-0000-000000000001', problemId: '00000000-0000-0000-0000-000000000001', isCorrect: true, time: 5 },
        { id: 2, student: '00000000-0000-0000-0000-000000000002', problemId: '00000000-0000-0000-0000-000000000002', isCorrect: false, time: 12 },
    ]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handleAddRow = () => {
        setRows([...rows, { id: Date.now(), student: '', problemId: '', isCorrect: false, time: 0 }]);
    };

    const handleDeleteRow = (id: number) => {
        setRows(rows.filter(r => r.id !== id));
    };

    const updateRow = (id: number, field: string, value: any) => {
        setRows(rows.map(r => r.id === id ? { ...r, [field]: value } : r));
    };

    const handleSubmit = async () => {
        setIsSubmitting(true);
        setMessage(null);
        try {
            // Transform rows to match backend schema: { student_id, question_id, is_correct, time_taken_seconds, notes }
            const payload = rows.map(r => ({
                student_id: r.student, // Must be UUID
                question_id: r.problemId, // Must be UUID
                is_correct: r.isCorrect,
                time_taken_seconds: r.time * 60,
                notes: "Bulk entry"
            }));

            const result = await cmsService.bulkSubmit(payload);

            if (result.failed_count > 0) {
                setMessage({ type: 'error', text: `제출 오류 발생. 성공: ${result.success_count}, 실패: ${result.failed_count}. UUID 형식을 확인하세요.` });
            } else {
                setMessage({ type: 'success', text: `성공적으로 ${result.success_count}건을 제출했습니다!` });
            }
        } catch (error: any) {
            console.error(error);
            setMessage({ type: 'error', text: error.response?.data?.detail || "제출 실패. 학생/문제 ID가 유효한 UUID인지 확인하세요." });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">대량 데이터 입력 (CMS)</Typography>
                <Box>
                    <Button variant="outlined" sx={{ mr: 1 }}>임시 저장</Button>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        startIcon={isSubmitting && <CircularProgress size={20} color="inherit" />}
                    >
                        {isSubmitting ? '제출 중...' : `일괄 제출 (${rows.length})`}
                    </Button>
                </Box>
            </Box>

            {message && (
                <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage(null)}>
                    {message.text}
                </Alert>
            )}

            <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
                <Table size="small">
                    <TableHead>
                        <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                            <TableCell>학생 UUID</TableCell>
                            <TableCell>문제 UUID</TableCell>
                            <TableCell align="center">정답 여부</TableCell>
                            <TableCell align="right">소요 시간 (분)</TableCell>
                            <TableCell align="center">작업</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rows.map((row) => (
                            <TableRow key={row.id}>
                                <TableCell>
                                    <TextField
                                        size="small" variant="standard" fullWidth
                                        value={row.student}
                                        onChange={(e) => updateRow(row.id, 'student', e.target.value)}
                                        placeholder="UUID"
                                    />
                                </TableCell>
                                <TableCell>
                                    <TextField
                                        size="small" variant="standard" fullWidth
                                        value={row.problemId}
                                        onChange={(e) => updateRow(row.id, 'problemId', e.target.value)}
                                        placeholder="UUID"
                                    />
                                </TableCell>
                                <TableCell align="center">
                                    <Checkbox
                                        checked={row.isCorrect}
                                        onChange={(e) => updateRow(row.id, 'isCorrect', e.target.checked)}
                                    />
                                </TableCell>
                                <TableCell align="right">
                                    <TextField
                                        size="small" variant="standard" type="number"
                                        value={row.time}
                                        onChange={(e) => updateRow(row.id, 'time', Number(e.target.value))}
                                        sx={{ width: 60 }}
                                    />
                                </TableCell>
                                <TableCell align="center">
                                    <IconButton size="small" onClick={() => handleDeleteRow(row.id)}><DeleteIcon /></IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <Button onClick={handleAddRow} sx={{ mt: 2 }}>+ 행 추가</Button>
        </Paper>
    );
};

// --- 2. Knowledge Map Mockup (Sunburst) ---
const mockSunburstData = {
    name: "Math Mastery",
    color: "hsl(0, 0%, 90%)",
    children: [
        {
            name: "Algebra",
            color: "#4caf50", // Green (Good)
            children: [
                { name: "Equations", color: "#4caf50", loc: 100 },
                { name: "Inequalities", color: "#81c784", loc: 80 } // Light Green
            ]
        },
        {
            name: "Geometry",
            color: "#ff9800", // Orange (Average)
            children: [
                { name: "Triangles", color: "#ffeb3b", loc: 60 }, // Yellow
                { name: "Circles", color: "#f44336", loc: 40 }   // Red (Weak)
            ]
        },
        {
            name: "Functions",
            color: "#2196f3", // Blue (Info)
            children: [
                { name: "Linear Func", color: "#64b5f6", loc: 70 },
                { name: "Quad Func", color: "#2196f3", loc: 90 }
            ]
        }
    ]
};

const KnowledgeMapMockup = () => {
    const [chartData, setChartData] = useState<any>(null);
    const demoStudentId = "00000000-0000-0000-0000-000000000001";

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await analyticsService.getUserReport(demoStudentId);
                // Try to use real map if available and has children
                if (res.data && res.data.mastery_map && res.data.mastery_map.children && res.data.mastery_map.children.length > 0) {
                    setChartData(res.data.mastery_map);
                } else {
                    // Fallback to mock if empty (e.g. no data yet)
                    console.log("No real data yet, using mock.");
                    setChartData(mockSunburstData);
                }
            } catch (e) {
                console.error("Failed to fetch mastery map", e);
                setChartData(mockSunburstData);
            }
        };
        fetchData();
    }, []);

    if (!chartData) return <CircularProgress />;

    return (
        <Paper sx={{ height: 600, p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6">지식 DNA 맵</Typography>
                <Button startIcon={<DownloadIcon />}>PDF 내보내기</Button>
            </Box>
            <Box sx={{ height: 500 }}>
                <ResponsiveSunburst
                    data={chartData}
                    margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                    id="name"
                    value="loc"
                    cornerRadius={2}
                    borderWidth={1}
                    borderColor="white"
                    colors={(node: any) => node.data.color || node.color} // Handle both structures
                    enableArcLabels={true}
                    arcLabel="id"
                    arcLabelsSkipAngle={10}
                    arcLabelsTextColor="black"
                />
            </Box>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
                <Chip label="취약 (<70%)" sx={{ bgcolor: '#f44336', color: 'white' }} />
                <Chip label="보통 (70-90%)" sx={{ bgcolor: '#ffeb3b' }} />
                <Chip label="숙달 (>90%)" sx={{ bgcolor: '#4caf50', color: 'white' }} />
            </Box>
        </Paper>
    );
};

// --- 3. Report Preview Mockup ---
const ReportPreviewMockup = () => {
    return (
        <Paper sx={{ p: 4, maxWidth: 800, mx: 'auto', bgcolor: 'white' }}>
            {/* Header */}
            <Box sx={{ borderBottom: '2px solid #333', pb: 2, mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <Box>
                    <Typography variant="h4" fontWeight="bold">주간 학습 리포트</Typography>
                    <Typography variant="subtitle1" color="text.secondary">학생: 김민수 | 기간: 2025-01-01 ~ 01-07</Typography>
                </Box>
                <Typography variant="h6" color="primary">Q-DNA Edu</Typography>
            </Box>

            {/* Summary */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid size={4}>
                    <Card sx={{ bgcolor: '#f5f5f5' }}>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>학습 시간</Typography>
                            <Typography variant="h5">5시간 30분</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid size={4}>
                    <Card sx={{ bgcolor: '#f5f5f5' }}>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>풀이 문제 수</Typography>
                            <Typography variant="h5">47</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid size={4}>
                    <Card sx={{ bgcolor: '#e3f2fd' }}>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>정답률</Typography>
                            <Typography variant="h5" color="primary">82% <Typography component="span" variant="body2" color="success.main">(+5%)</Typography></Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Analysis */}
            <Typography variant="h6" gutterBottom sx={{ borderLeft: '4px solid #4caf50', pl: 1 }}>🎯 강점 및 약점 분석</Typography>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid size={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold" color="success.main">주요 강점</Typography>
                        <ul style={{ paddingLeft: 20, margin: '10px 0' }}>
                            <li>이차방정식 (95%)</li>
                            <li>함수 (88%)</li>
                        </ul>
                    </Paper>
                </Grid>
                <Grid size={6}>
                    <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fff3e0' }}>
                        <Typography variant="subtitle1" fontWeight="bold" color="error">핵심 취약점</Typography>
                        <ul style={{ paddingLeft: 20, margin: '10px 0' }}>
                            <li>삼각형의 성질 (45%)</li>
                            <li><strong>원인:</strong> 초등 기하 기초 부족 (G5)</li>
                        </ul>
                    </Paper>
                </Grid>
            </Grid>

            {/* Prediction */}
            <Typography variant="h6" gutterBottom sx={{ borderLeft: '4px solid #2196f3', pl: 1 }}>📈 AI 점수 예측</Typography>
            <Box sx={{ p: 3, bgcolor: '#fafafa', borderRadius: 2, textAlign: 'center', mb: 4 }}>
                <Typography variant="body1">현재 학습 추세 기반 예측:</Typography>
                <Typography variant="h3" color="primary" sx={{ my: 2 }}>80 ~ 85 점</Typography>
                <Typography variant="body2" color="text.secondary">목표 점수: 85 점 (달성 확률 92%)</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                <Button
                    variant="contained"
                    startIcon={<SendIcon />}
                    onClick={async () => {
                        try {
                            alert("PDF 생성 중...");
                            // Use a dummy UUID for demo
                            const blob = await reportService.generate("00000000-0000-0000-0000-000000000001");
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = "report.pdf";
                            a.click();
                        } catch (e) {
                            alert("리포트 생성 실패");
                            console.error(e);
                        }
                    }}
                >
                    리포트 PDF 생성 및 다운로드
                </Button>
            </Box>
        </Paper>
    );
};

export default function MvpMockupPage() {
    const [tabIndex, setTabIndex] = useState(0);

    const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
        setTabIndex(newValue);
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>Q-DNA MVP 기능 목업</Typography>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabIndex} onChange={handleChange}>
                    <Tab label="1. 대량 입력 (CMS)" />
                    <Tab label="2. 지식 맵 (시각화)" />
                    <Tab label="3. 자동 리포트 (PDF)" />
                </Tabs>
            </Box>
            <TabPanel value={tabIndex} index={0}>
                <BulkInputMockup />
            </TabPanel>
            <TabPanel value={tabIndex} index={1}>
                <KnowledgeMapMockup />
            </TabPanel>
            <TabPanel value={tabIndex} index={2}>
                <ReportPreviewMockup />
            </TabPanel>
        </Container>
    );
}
