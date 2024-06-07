const api = "http://127.0.0.1:5000";

window.onload = () => {
    // Αλληλεπίδραση 1: Σύνδεση του κουμπιού αναζήτησης με τη λειτουργία searchButtonOnClick
    document.getElementById("searchButton").addEventListener("click", searchButtonOnClick);

    // Αλληλεπίδραση 2: Σύνδεση της φόρμας προσθήκης προϊόντος με τη λειτουργία productFormOnSubmit
    document.getElementById("addProductFrame").addEventListener("submit", productFormOnSubmit);
}

searchButtonOnClick = async () => {
    // Αλληλεπίδραση 1: Αναζήτηση προϊόντος
    const searchInput = document.getElementById("searchInput").value;
    const resultsTableBody = document.querySelector(".data-table tbody");

    // Καθαρισμός προηγούμενων αποτελεσμάτων
    resultsTableBody.innerHTML = "";

    if (searchInput.trim() === "") {
        alert("Please enter a search term");
        return;
    }

    try {
        const response = await fetch(`${api}/search?name=${encodeURIComponent(searchInput)}`);
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        const results = await response.json();

        // Προσθήκη αποτελεσμάτων στον πίνακα
        results.forEach(product => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.production_year}</td>
                <td>${product.price}</td>
                <td>${product.color}</td>
                <td>${product.size}</td>
            `;
            resultsTableBody.appendChild(row);
        });
    } catch (error) {
        console.error("There was a problem with the fetch operation:", error);
    }
}

productFormOnSubmit = async (event) => {
    // Αλληλεπίδραση 2: Προσθήκη προϊόντος
    event.preventDefault(); // Αποφυγή υποβολής φόρμας

    const name = document.getElementById("name").value;
    const productionYear = document.getElementById("production-year").value;
    const price = document.getElementById("price").value;
    const color = document.getElementById("color").value;
    const size = document.getElementById("size").value;

    if (!name || !productionYear || !price || !color || !size) {
        alert("Please fill in all fields");
        return;
    }

    const productData = {
        name: name,
        production_year: parseInt(productionYear),
        price: parseFloat(price),
        color: color,
        size: size
    };

    try {
        const response = await fetch(`${api}/add-product`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(productData)
        });

        if (!response.ok) {
            throw new Error("Network response was not ok");
        }

        const result = await response.json();
        if (result.status === "success") {
            // Καθαρισμός πεδίων φόρμας
            document.getElementById("name").value = "";
            document.getElementById("production-year").value = "";
            document.getElementById("price").value = "";
            document.getElementById("color").value = "";
            document.getElementById("size").value = "";

            alert("ΟΚ");
        } else {
            alert("Failed to add product");
        }
    } catch (error) {
        console.error("There was a problem with the fetch operation:", error);
    }
}
