//This throws an exception, Watch out !

export async function getClientId() {
    try {
        console.log("pleeeeeeeeeeeeeeeeeeeeeeeeeeeease 1")
        const response = await fetch("/api/auth/getId/", {
            method: "GET",
            credentials: "include",
        });
        console.log("pleeeeeeeeeeeeeeeeeeeeeeeeeeeease 2");
        const data = await response.json();
        if (!response.ok) {
            console.log("Response isnt ok !");
            return null;
        }
        console.log("data:", data);
        if (data.client_id) {
            return data.client_id;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.log("pleeeeeeeeeeeeeeeeeeeeeeeeeeeease")
        console.error("Erreur lors de la récupération de l'ID :", error);
        return null;
    }
}