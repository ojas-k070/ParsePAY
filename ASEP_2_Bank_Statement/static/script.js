document.addEventListener('DOMContentLoaded', () => {
    const introSection = document.querySelector('#intro-section');
    const contentSection = document.querySelector('#content-section');
    const fileInput = document.querySelector('#fileInput');
    const uploadForm = document.querySelector('#uploadForm');
    const feedbackDiv = document.querySelector('#feedback');

    // Show the main content when the user clicks on the intro section
    introSection.addEventListener('click', () => {
        introSection.style.display = 'none'; // Hide the intro section
        contentSection.style.display = 'block'; // Show the content section
        document.body.style.height = 'auto'; // Allow the page to scroll if needed
    });

    // File selection message display
    fileInput.addEventListener('change', () => {
        const fileName = fileInput.value.split('\\').pop();
        if (fileName) {
            displayMessage(`File selected: ${fileName}`, 'success');
        }
    });

    function displayMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = type === 'error' ? 'alert alert-danger' : 'alert alert-success';
        messageDiv.textContent = message;
        feedbackDiv.appendChild(messageDiv);

        setTimeout(() => {
            if (feedbackDiv.contains(messageDiv)) {
                feedbackDiv.removeChild(messageDiv);
            }
        }, 5000);
    }
});
