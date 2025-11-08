const API_ROOT_URL = "http://localhost:8000"; 

export const fetchMusic = async () => { 
    try {
        const res = await fetch(`${API_ROOT_URL}/music`, {
            method: "GET",
        });

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.url;

    } catch (error) {
        throw new Error(`Failed to fetch music: ${error.message}`);
    }
};