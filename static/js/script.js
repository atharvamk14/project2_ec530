document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            alert('Form submitted!');  // Replace this with more meaningful interaction as needed
        });
    });
});
