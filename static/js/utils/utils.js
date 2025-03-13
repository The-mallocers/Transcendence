//This throws an exception, Watch out !
export async function getClientId() {
    try {
        const response = await fetch("/api/client/getId", {
            method: "GET",
            credentials: "include",
        });
        const data = await response.json();
        console.log("in getclientid, result is:", data.client_id);
        if (data.client_id) {
            return data.client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}