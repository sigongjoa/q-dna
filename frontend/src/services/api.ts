import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
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

export default api;
