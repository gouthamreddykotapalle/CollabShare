//basic functions

function logout() {
    //set cookie and redirect
    document.cookie = "userID=";
    window.location.href = 'https://s3.amazonaws.com/frontend.noteshare/index.html';
}

function populateGroupsDropdown() {


    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var params = {
        'q': docCookies.getItem('userID')
    };
    var body = "";
    var additionalParams = "";
    var groups;
    apigClient.groupGet(params, body, additionalParams).then(function(result) {
        var dropdown = document.getElementsByClassName('groups-dropdown-menu')[0]
        if (dropdown) {
            var groups = result.data;
            groups.forEach(function(group) {
                var li = document.createElement('li')
                var a = document.createElement('a')
                a.text = group['groupName']
                a.value = group['groupId']
                a.setAttribute('id', group['groupId']);
                a.setAttribute('href', '#');
                li.setAttribute('value', group['groupId'])
                li.appendChild(a);
                dropdown.appendChild(li);

                $("#" + group['groupId']).click(function() {
                    $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
                    document.getElementById('dropdownMenu1').value = $(this)[0].id;
                });
            });

        }

        //populate the dropdown div
    }).catch(function(result) {
        // Add error callback code here.
    });

}

function login() {
    //TO DO: Modify redirect URI post hosting on S3 //if not logged in, just stay here and do not redirect, redirect when button is clicked
    window.location.href = 'https://noteshare.auth.us-east-1.amazoncognito.com/login?client_id=1962ro47nqjq5nreds0et30e6a&response_type=token&scope=aws.cognito.signin.user.admin+email+login/login+openid+phone+profile&redirect_uri=https://s3.amazonaws.com/frontend.noteshare/index.html';

}