import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Box, Paper, Typography, Button, Stepper, Step, StepLabel, StepContent,
    Alert, CircularProgress, Chip, Divider, Container
} from '@mui/material';
import BugReportIcon from '@mui/icons-material/BugReport';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import { questionService } from '../services/api';

// Types for the API response
interface SolutionStep {
    step: number;
    content: string;
    formula?: string;
    is_error: boolean;
    error_type?: string;
    error_explanation?: string;
}

interface ClinicData {
    erroneous_solution: {
        steps: SolutionStep[];
        final_wrong_answer: string;
    };
    correct_solution: {
        steps: SolutionStep[];
    };
}

export default function MisconceptionClinic() {
    const { questionId } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [questionContent, setQuestionContent] = useState<string>("");
    const [clinicData, setClinicData] = useState<ClinicData | null>(null);
    const [selectedStepIndex, setSelectedStepIndex] = useState<number | null>(null);
    const [revealAnswer, setRevealAnswer] = useState(false);
    const [feedback, setFeedback] = useState<{ msg: string, type: 'success' | 'error' | 'info' } | null>(null);

    // Initial Load: Fetch Question & Generate Misconception Scenario
    useEffect(() => {
        if (!questionId) return;
        initializeClinic();
    }, [questionId]);

    const initializeClinic = async () => {
        setLoading(true);
        setFeedback(null);
        setRevealAnswer(false);
        setSelectedStepIndex(null);

        try {
            // 1. Get Question Text
            const qData = await questionService.getById(questionId!);
            setQuestionContent(qData.content_stem);

            // 2. Generate Misconception Scenario (Using JSON response)
            // We pass 'output_format=json' implicitly by not asking for blob/pdf in a custom call
            // We need to extend the API service lightly or just make a direct call here for JSON
            // But let's assume we use a specific call or modify the service a bit. 
            // Actually, the previous API.ts changes returned blob for generateErrorWorksheet.
            // Let's assume we add a new method or use raw axios for JSON here.

            // Temporary direct fetch for JSON mode
            const response = await fetch(
                `http://localhost:8000/api/v1/questions/${questionId}/erroneous-solution?output_format=json`,
                { method: 'POST' }
            );
            const data = await response.json();
            setClinicData(data);

        } catch (error) {
            console.error("Clinic Load Failed", error);
            setFeedback({ msg: "Failed to load clinic data.", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    const handleStepClick = (index: number, step: SolutionStep) => {
        if (revealAnswer) return; // Already solved

        setSelectedStepIndex(index);

        if (step.is_error) {
            setFeedback({
                msg: `✅ 정답입니다! 이 단계에서 오류가 발생했습니다. (${step.error_type} 감지)`,
                type: 'success'
            });
            setRevealAnswer(true);
        } else {
            setFeedback({
                msg: "🤔 이 단계는 논리적으로 올바릅니다. 다른 의심가는 부분을 찾아보세요.",
                type: 'error'
            });
        }
    };

    const handleDownloadPDF = async () => {
        if (!questionId) return;
        setLoading(true); // Reuse loading state or create new one? Better create new one or use feedback
        // Let's create a local loading indicator just for button if we had one, but reuse global loading for now or just generic
        // Actually simplest is to just not block UI too much but show logic.
        // Let's use a temporary feedback
        setFeedback({ msg: "PDF 생성 중입니다... (시간이 조금 걸릴 수 있습니다)", type: "info" });

        try {
            const pdfBlob = await questionService.generateErrorWorksheet(questionId, []);
            const url = window.URL.createObjectURL(pdfBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `misconception_clinic_${questionId}.pdf`;
            document.body.appendChild(a); // Vital for some browsers
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            setFeedback({ msg: "PDF 다운로드가 완료되었습니다.", type: "success" });
        } catch (e) {
            console.error(e);
            setFeedback({ msg: "PDF 생성 실패: backend/Ollama 연결을 확인하세요.", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 10, gap: 2 }}>
                <CircularProgress size={60} color="warning" />
                <Typography variant="h6">AI가 학생의 흔한 실수를 시뮬레이션 중입니다...</Typography>
                <Typography variant="caption" color="text.secondary">Ollama (qwen2.5) Generating...</Typography>
            </Box>
        );
    }

    if (!clinicData) return <Alert severity="error">데이터를 불러오지 못했습니다.</Alert>;

    const errorStep = clinicData.erroneous_solution.steps.find(s => s.is_error);

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
                <BugReportIcon color="warning" sx={{ fontSize: 40 }} />
                <Box>
                    <Typography variant="h4" fontWeight="bold">오개념 클리닉 (Misconception Clinic)</Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                        AI가 생성한 '실수하기 쉬운 풀이'를 보고, 어느 부분이 틀렸는지 찾아보세요.
                    </Typography>
                </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 4, flexDirection: { xs: 'column', md: 'row' } }}>
                {/* Left Panel: Problem & Erroneous Solution */}
                <Box sx={{ flex: 1 }}>
                    <Paper elevation={3} sx={{ p: 3, mb: 3, bgcolor: '#fffde7' }}>
                        <Typography variant="h6" gutterBottom>📝 문제</Typography>
                        <Typography variant="body1" sx={{ fontSize: '1.1rem', whiteSpace: 'pre-wrap' }}>
                            {questionContent}
                        </Typography>
                    </Paper>

                    <Paper elevation={3} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom color="error.main">
                            ❌ 학생의 오답 풀이
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                            아래 풀이 단계 중 <strong>틀린 부분</strong>을 클릭하세요!
                        </Typography>

                        <Stepper orientation="vertical" nonLinear>
                            {clinicData.erroneous_solution.steps.map((step, index) => (
                                <Step key={index} active={true}>
                                    <StepLabel
                                        error={revealAnswer && step.is_error}
                                        icon={revealAnswer && step.is_error ? <ErrorIcon color="error" /> : undefined}
                                        onClick={() => handleStepClick(index, step)}
                                        sx={{
                                            cursor: revealAnswer ? 'default' : 'pointer',
                                            '&:hover': { bgcolor: revealAnswer ? 'transparent' : '#f5f5f5' },
                                            p: 1, borderRadius: 1
                                        }}
                                    >
                                        <Typography variant="subtitle1" fontWeight="bold">
                                            Step {step.step}
                                        </Typography>
                                    </StepLabel>
                                    <StepContent>
                                        <Typography>{step.content}</Typography>
                                        {step.formula && (
                                            <Paper variant="outlined" sx={{ mt: 1, p: 1, bgcolor: '#f0f0f0', fontFamily: 'monospace' }}>
                                                {step.formula}
                                            </Paper>
                                        )}
                                    </StepContent>
                                </Step>
                            ))}
                        </Stepper>

                        <Box sx={{ mt: 3, p: 2, borderTop: '1px dashed #ccc', textAlign: 'center' }}>
                            <Typography variant="h6" color="error">
                                ∴ 최종 답: {clinicData.erroneous_solution.final_wrong_answer}
                            </Typography>
                        </Box>
                    </Paper>
                </Box>

                {/* Right Panel: Feedback & Correction */}
                <Box sx={{ flex: 1 }}>
                    {feedback && (
                        <Alert
                            severity={feedback.type}
                            sx={{ mb: 3, fontSize: '1.1rem' }}
                            icon={feedback.type === 'success' ? <CheckCircleIcon fontSize="inherit" /> : <ErrorIcon fontSize="inherit" />}
                        >
                            {feedback.msg}
                        </Alert>
                    )}

                    {revealAnswer && errorStep && (
                        <Paper elevation={4} sx={{ p: 3, border: '2px solid #66bb6a' }}>
                            <Typography variant="h5" color="success.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <CheckCircleIcon /> 오개념 분석 완료
                            </Typography>

                            <Box sx={{ mt: 2, mb: 3 }}>
                                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                                    발견된 오류 유형
                                </Typography>
                                <Chip label={errorStep.error_type || "알 수 없는 오류"} color="error" sx={{ fontSize: '1rem', px: 1, py: 0.5 }} />
                            </Box>

                            <Box sx={{ mb: 3, bgcolor: '#e8f5e9', p: 2, borderRadius: 2 }}>
                                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                                    💡 AI 선생님의 해설
                                </Typography>
                                <Typography variant="body1">
                                    {errorStep.error_explanation}
                                </Typography>
                            </Box>

                            <Divider sx={{ my: 3 }}>올바른 풀이</Divider>

                            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                                {clinicData.correct_solution.steps.map((step, idx) => (
                                    <Box key={idx} sx={{ mb: 2 }}>
                                        <Typography variant="subtitle2" color="primary">Step {step.step}</Typography>
                                        <Typography variant="body2">{step.content}</Typography>
                                        {step.formula && <code>{step.formula}</code>}
                                    </Box>
                                ))}
                            </Box>

                            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                                <Button
                                    variant="outlined"
                                    startIcon={<RefreshIcon />}
                                    onClick={initializeClinic}
                                    fullWidth
                                >
                                    다른 오류로 다시하기
                                </Button>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    startIcon={<DownloadIcon />}
                                    onClick={handleDownloadPDF}
                                    fullWidth
                                >
                                    워크시트 PDF 저장
                                </Button>
                            </Box>
                        </Paper>
                    )}
                </Box>
            </Box>
        </Container>
    );
}
