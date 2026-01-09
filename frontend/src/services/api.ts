import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface CurriculumNode {
    node_id: number;
    name: string;
    path: string;
    children: CurriculumNode[];
}

export const curriculumService = {
    getTree: async () => {
        const response = await api.get<CurriculumNode[]>('/curriculum/tree');
        return response.data;
    },
};

export const taggingService = {
    suggest: async (text: string) => {
        const response = await api.get('/tags/suggest', { params: { text } });
        return response.data;
    },
};

export const analyticsService = {
    submitAttempt: async (data: any) => {
        return await api.post('/analytics/attempt', data);
    },
    getUserReport: async (userId: string) => {
        return await api.get(`/analytics/report/${userId}`);
    }
};

export const questionService = {
    // Analyze question content to extract metadata
    analyze: async (content_stem: string) => {
        const response = await api.post('/questions/analyze', { content_stem });
        return response.data;
    },
    // Generate a twin question
    createTwin: async (questionId: string) => {
        const response = await api.post(`/questions/${questionId}/twin`);
        return response.data;
    },
    // Create new question (Save)
    create: async (payload: any) => {
        const response = await api.post('/questions/', payload);
        return response.data;
    },
    // Get all questions (with optional skip/limit logic if needed later)
    getAll: async () => {
        const response = await api.get('/questions/');
        return response.data;
    },
    // Get single question by ID
    getById: async (id: string) => {
        const response = await api.get(`/questions/${id}`);
        return response.data;
    },
    // Generate Error Worksheet (PDF)
    generateErrorWorksheet: async (
        questionId: string,
        errorTypes?: string[]
    ): Promise<Blob> => {
        const params = new URLSearchParams();
        if (errorTypes) {
            errorTypes.forEach(et => params.append('error_types', et));
        }
        params.append('output_format', 'pdf');

        const response = await api.post(
            `/questions/${questionId}/erroneous-solution?${params.toString()}`,
            {},
            { responseType: 'blob' }
        );

        return response.data; // axios returns data as blob because of responseType
    }
};

export const diagramService = {
    async generate(description: string): Promise<{ image_url: string }> {
        const response = await api.post('/diagrams/generate', { description });
        return response.data;
    }
};

export const cmsService = {
    bulkSubmit: async (attempts: any[]) => {
        const response = await api.post('/cms/bulk-submit', { items: attempts });
        return response.data;
    }
};

export const reportService = {
    generate: async (studentId: string) => {
        // Return blob for PDF download
        const response = await api.post(`/reports/generate/${studentId}`, {}, { responseType: 'blob' });
        return response.data;
    }
};

export default api;
