function getDocuments(groupid) {
    //aws call to fetch all groups
    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var params = {
        'userID': "", //change this
        'groupID': groupid, //change this
        "q": ""
    };
    var body = "";
    var additionalParams = "";
    console.log("Testing getDocuments");
    apigClient.documentGet(params, body, additionalParams).then(function(result) {
        var documents = result.data;
        console.log(documents);
        console.log("hello");
        var list = document.getElementById("listdocs");
        console.log(list);
        documents.forEach(function(document) {
            //fill up code
            //createGroupDiv(group);
            console.log(document);
            // str = '<a href="http://localhost:5501/document.html?q="'+document.documentId+' class="list-group-item" id="'+document.documentId+'">'+document.name+'</a>';
            // console.log(str);
            // list.innerHTML += str;
            createGroupli(document, list);
        });
    }).catch(function(result) {
        // Add error callback code here.
    });
}

function createGroupli(document, templateDiv) {
    console.log("document=" + document.name);
    var itm = templateDiv.getElementsByTagName('a')[0];
    var elem = itm.cloneNode(true);
    elem.setAttribute('class', 'list-group-item');
    elem.setAttribute('href', 'https://s3.amazonaws.com/frontend.noteshare/document.html?q=' + document.documentId);
    elem.getElementsByTagName('div')[0].innerHTML = document.name;
    elem.setAttribute('id', document.documentId);
    elem.style.display = "block";

    // var deleteIconDiv = elem.getElementsByClassName('group-delete-icon')[0];

    // deleteIconDiv.onclick = deleteGroup;
    if (templateDiv)
        templateDiv.appendChild(elem);
}

function deleteDocument() {
    //aws call to fetch all groups
    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var params = {
        'userID': "Google_115232286070042015037", //change this
        'groupID': "sdsdasd" //change this
    };
    var body = "";
    var additionalParams = "";
    var groups;
    apigClient.documentDocumentIdDelete(params, body, additionalParams).then(function(result) {
        var documents = result.data;
        console.log(documents);
        documents.forEach(function(document) {
            //fill up code
            //createGroupDiv(group);
        });
    }).catch(function(result) {
        // Add error callback code here.
    });
}


function getPages() {
    //aws call to fetch all groups
    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var params = {
        'userID': "Google_115232286070042015037", //change this
        'groupID': "sdsdasd" //change this
    };
    var body = "";
    var additionalParams = "";
    var groups;
    apigClient.documentDocumentIdGet(params, body, additionalParams).then(function(result) {
        var documents = result.data;
        console.log(documents);
        documents.forEach(function(document) {
            //fill up code
            //createGroupDiv(group);
        });
    }).catch(function(result) {
        // Add error callback code here.
    });
}


function createGroup() {
    var elems = document.getElementsByClassName('form-group')[0]
    if (elems.style.display == "none") {
        elems.setAttribute('style', 'display: block')
    } else {
        var name = elems.getElementsByClassName('group-name')[0].value
        var members = elems.getElementsByClassName('group-members')[0].value
        var desc = elems.getElementsByClassName('group-desc')[0].value
        //submitting the form
        //redirect as required

        var apigClient = apigClientFactory.newClient();
        var apigClient = apigClientFactory.newClient({
            accessKey: 'AKIASYXCMKIIJ7CBXGDV',
            secretKey: '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',
        });

        var body = { 'groupName': name, 'description': desc, 'emailIds': members.split(','), 'ownerEmailID': docCookies.getItem('email'), 'ownerID': docCookies.getItem('userID') }
        var params = {}
        var additionalParams = {}
        apigClient.groupPost(params, body, additionalParams).then(function(result) {
            var data = result.data;
            createGroupDiv(result.data);

        }).catch(function(result) {
            // Add error callback code here.
        });

        /*
        var xhr = new XMLHttpRequest();
        xhr.addEventListener("readystatechange", function () {//adding the event listener
            if (this.readyState === 4) {
                console.log(this);
                //can update corresponding div on this page itself
            }
        });

        xhr.open("POST", "https://gdo5vwxsh1.execute-api.us-east-1.amazonaws.com/test/creategroup");
        xhr.setRequestHeader('Authorization', docCookies.getItem('access_token'))
        var data;   
        xhr.send(data);*/
    }
}


function loadGroups() {
    //aws call to fetch all groups
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
        var groups = result.data;
        groups.forEach(function(group) {
            //fill up code
            createGroupDiv(group);
        });
    }).catch(function(result) {
        // Add error callback code here.
    });
}


function createGroupDiv(group) {
    var templateDiv = document.getElementById('template-group-item-div')
    var elem = templateDiv.cloneNode(true)
    elem.setAttribute('class', 'list-group-item list-group-item-action');
    elem.setAttribute('id', group['groupId'])
    elem.setAttribute('style', 'visibility:visible;height:100px;');

    var groupNameDiv = elem.getElementsByClassName('group-name')[0]
    var groupDescriptionDiv = elem.getElementsByClassName('group-description')[0]
    var deleteIconDiv = elem.getElementsByClassName('group-delete-icon')[0]
    var peopleIconDiv = elem.getElementsByClassName('group-users-icon')[0]
    var notesIconDiv = elem.getElementsByClassName('group-notes-icon')[0]

    groupNameDiv.innerHTML = group['groupName']
    groupNameDiv.onclick = groupSelected;

    deleteIconDiv.onclick = deleteGroup;
    notesIconDiv.onclick = listNotes;
    peopleIconDiv.onclick = listUsers;

    var check = doesGroupBelongToCurrentUser(group);
    if (!check)
        elem.removeChild(deleteIconDiv)


    groupDescriptionDiv.innerHTML = group['description']

    var parent = document.getElementById('group-list')
    if (parent)
        parent.appendChild(elem)
}


function groupSelected(e) {
    var id = e.target.parentElement.id;
    //redirect as required to list notes belonging to that group
    getDocuments(id);
}


function listUsers(e) {
    //redirect to users of a particular goup page
    var id = e.target.parentElement.parentElement.parentElement.id;
    window.location.href = "https://s3.amazonaws.com/frontend.noteshare/users.html?groupId=" + id;
}

function listNotes(e) {
    //redirect to notes associated with a particular group
}

function doesGroupBelongToCurrentUser(group) {
    return docCookies.getItem('userID') == group['owner'];
}

function deleteGroup(e) {
    var id = e.target.parentElement.parentElement.parentElement.id;
    //aws call to delete id and update UI
    //delete from ui
    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var groupId = id;
    var params = {
        'groupId': id,
    };
    var body = "";
    var additionalParams = "";
    var groups;
    apigClient.groupDelete(params, body, additionalParams).then(function(result) {
        var elem = document.getElementById(id)
        var parent = elem.parentElement
        parent.removeChild(elem);
    }).catch(function(result) {
        // Add error callback code here.
    });
}