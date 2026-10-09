import api from "./api";

export function detect(file, crop) {
  const form = new FormData();
  form.append("file", file);
  form.append("crop", crop);
  return api.post("/disease/detect", form).then((r) => r.data);
}
export const getModelStatus = () => api.get("/disease/model-status").then((r) => r.data);
export const getHistory = () => api.get("/disease/history").then((r) => r.data);
export const getResult = (id) => api.get(`/disease/${id}`).then((r) => r.data);
export const deleteResult = (id) => api.delete(`/disease/${id}`);
