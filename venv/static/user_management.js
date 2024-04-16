$(document).ready(function() {
    // Function to fetch users from Flask API
    function getUsers() {
        $.ajax({
            url: '/api/users',
            type: 'GET',
            success: function(users) {
                // Render users on the page
                renderUsers(users);
            },
            error: function(error) {
                console.error('Error fetching users:', error);
            }
        });
    }

    // Function to render users on the page
    function renderUsers(users) {
        var userList = $('#user-list');
        userList.empty(); // Clear existing content

        // Check if users array is empty
        if (users.length === 0) {
            userList.append('<p>No users found.</p>');
        } else {
            // Loop through users and append to user list
            users.forEach(function(user) {
                userList.append('<p>Username: ' + user.Username + ', Email: ' + user.Email + '</p>');
            });
        }
    }

    // Call getUsers function when the page loads
    getUsers();

    // Submit event handler for add user form
    $('#add-user-form').submit(function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form data
        var formData = {
            username: $('#username').val(),
            email: $('#email').val(),
            password: $('#password').val()
        };

        // Add user using AJAX
        $.ajax({
            url: '/api/users',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                console.log('User added successfully:', response);
                // After adding user, fetch updated user list
                getUsers();
                // Reset form fields
                $('#username').val('');
                $('#email').val('');
                $('#password').val('');
            },
            error: function(error) {
                console.error('Error adding user:', error);
            }
        });
    });
});
