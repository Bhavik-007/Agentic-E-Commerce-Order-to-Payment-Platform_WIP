import { api } from "./api";

export const askAssistant = async (message) => (await api.post("/assistant/chat", { message })).data;
