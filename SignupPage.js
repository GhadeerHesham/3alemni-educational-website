document
    .getElementById("signupForm")
    .addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent the form from submitting traditionally

        // Get the selected role
        const roleSelect = document.getElementById("roleSelect");
        const selectedRole = roleSelect.value;

        // Redirect based on the selected role
        if (selectedRole === "Student") {
            window.location.href = "StudentDashboard_Overview.html";
        } else if (selectedRole === "Teacher") {
            window.location.href = "TeacherDashboard_Overview.html";
        } else if (selectedRole === "Assistant") {
            window.location.href = "assistantdashboard.html";
        } else {
            alert("Please select a role!"); // Show an alert if no role is selected
        }
    });