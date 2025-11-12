import axios from 'axios';
import { Node, QueueEntry } from './types';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api',
  withCredentials: true,
});

export async function getStructure(): Promise<Node[]> {
  const { data } = await client.get('/structure/');
  return data;
}

export async function getQueue(): Promise<QueueEntry[]> {
  const { data } = await client.get('/queue/');
  return data;
}

export async function completeRegistration(userId: number): Promise<void> {
  await client.post('/complete/', { user_id: userId });
}
