var queue = [];

function send(e) {
    var upload_status = document.getElementById("status");
    upload_status.innerHTML = "Uploading...";
    var uuid = create_UUID();
    uuid = uuid.toString();
    var img_array = document.getElementById('js-upload-files').files;

    var status = setInterval(() => {
        if (queue.length == img_array.length) {
            var groupId = document.getElementById('dropdownMenu1').value;
            NotifyLambdaApiGet(uuid, img_array.length, upload_status, groupId);
            clearInterval(status);
        } else {
            console.log(queue.length);
        }
    }, 1000);

    var albumBucketName = "pages.noteshare";
    var bucketRegion = "us-east-1";
    var IdentityPoolId = "us-east-1:2db3f5b2-72a8-4466-884a-88cfcf8799a8";

    AWS.config.update({
        region: bucketRegion,
        credentials: new AWS.CognitoIdentityCredentials({
            IdentityPoolId: IdentityPoolId
        })
    });

    var s3 = new AWS.S3({
        apiVersion: "2006-03-01",
        params: { Bucket: albumBucketName }
    });

    for (var i = 0; i < img_array.length; i++) { //i will be the page number
        var img = img_array[i];
        console.log(img);

        var params = {
            Bucket: albumBucketName,
            Key: uuid + "_" + i.toString() + ".png",
            Body: img,
            ACL: 'private',
            ContentType: 'img/png',
            Metadata: {
                'documentID': uuid + i.toString() + ".png",
                'pageNumber': i.toString()
            }
        };

        s3.upload(params, function(err, data) {
            if (err)
                console.log(err);
            else {
                queue.push(data.Key);
                console.log(data.Key);
                console.log("i=" + i.toString());
                str = '<a href="#" class="list-group-item list-group-item-success"><span class="badge alert-success pull-right">Success</span>' + uuid + '_' + queue.length.toString() + '.png' + '</a>'
                var finished = document.getElementById("finished");
                finished.innerHTML += str;
            }
        });
    }
}

function NotifyLambdaApiGet(uuid, pages, upload_status, groupId) {
    //Make a get request to the the url/serch route defined in the API gateway
    var data = {
        "documentID": uuid,
        "noOfPages": pages,
        "documentName": document.getElementById("docname").value, //change this
        "description": "description", //change this
        "ownerId": docCookies.getItem('userID'), //change this
        "ownerName": "owner name", //change this
        "groupIds": [
            //"97c711f4-1baf-11ea-a998-e7f31c0ffa8c" //change this
            groupId
        ]
    };

    var xhr = new XMLHttpRequest();

    xhr.addEventListener("readystatechange", function() { //adding the event listener
        if (this.readyState === 4) {
            console.log(this.responseText);
            var data = JSON.parse(this.responseText);
            console.log(data);
            upload_status.innerHTML = "Uploaded successfully";
        }
    });

    xhr.open("POST", "https://dps1go8r4l.execute-api.us-east-1.amazonaws.com/Test/document");
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify(data));
}

function create_UUID() {
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random() * 16) % 16 | 0;
        dt = Math.floor(dt / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

function deleteDoc() {
    //delete call to the /docuement route

}

function getDoc() {
    //get call to the /document route

}

function clearDiv(d, dont_delete) {
    var topDiv = document.getElementById(d);
    var children = topDiv.getElementsByTagName('a');
    var len = children.length;
    for (var i = 0; i < len - 1; i++) {
        var currChild = children[children.length - 1];
        if (currChild.id != dont_delete) {
            topDiv.removeChild(currChild);
        }
    }
}

function clearImageDiv(d) {
    var topDiv = document.getElementById(d);
    var children = topDiv.getElementsByTagName('img');
    var len = children.length;
    for (var i = 0; i < len; i++) {
        var currChild = children[0];
        topDiv.removeChild(currChild);
    }
}

function getsearchres(e) {


    var apigClient = apigClientFactory.newClient();
    var apigClient = apigClientFactory.newClient({
        accessKey: 'AKIASYXCMKIIJ7CBXGDV',
        secretKey: '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',
    });

    var params = {
        'q': document.getElementById("searchtext").value,
        'userID': docCookies.getItem("userID")
    };
    var body = "";
    var additionalParams = "";


    if (e.key == "Enter") {

        clearDiv("listlinks", "template-listlinks");
        clearDiv("listdocs", "template-listdocs");
        clearImageDiv("imageResults");

        console.log("as");
        apigClient.searchGet(params, body, additionalParams).then(function(result) {
            console.log(result);

            var links = result['data']["stackOverflowLinks"];
            links.forEach(function(link) {
                //fill up code
                console.log(link);
                var main = document.getElementById("listlinks");
                var itm = main.getElementsByTagName('a')[0];
                var elem = itm.cloneNode(true);
                elem.setAttribute('class', 'list-group-item');
                elem.setAttribute('href', link);
                elem.setAttribute('id', '');
                elem.getElementsByTagName('div')[0].innerHTML = link;
                elem.style.display = "block";
                main.appendChild(elem);
            });


            var docs = result['data']["documents"];
            docs.forEach(function(doc) {
                //fill up code
                console.log(doc);
                var main = document.getElementById("listdocs");
                var itm = main.getElementsByTagName('a')[0];
                var elem = itm.cloneNode(true);
                elem.setAttribute('class', 'list-group-item');
                elem.setAttribute('href', 'https://s3.amazonaws.com/frontend.noteshare/document.html?q=' + doc.documentId);
                elem.setAttribute('id', doc.documentId);
                elem.getElementsByTagName('div')[0].innerHTML = doc.documentName;
                elem.style.display = "block";
                main.appendChild(elem);
            });


            var docs = result['data']["pages"];
            docs.forEach(function(page) {
                //fill up code
                console.log(page);
                var imgDiv = document.getElementById("imageResults");
                var s3ImgPath = "https://s3.amazonaws.com/pages.noteshare/" + page.pageId + ".png"; //change this
                var elem = document.createElement("img");
                elem.setAttribute('src', s3ImgPath);
                elem.setAttribute('onclick', "redirect(event)");
                elem.setAttribute("style", "height: 300px; width: 300px;");
                elem.setAttribute('class', 'imgClass')
                elem.setAttribute('id', page.pageId);
                imgDiv.appendChild(elem);
            });



        }).catch(function(result) {
            // Add error callback code here.
            console.log(result);
        });
    }

}


function redirect(e) {
    console.log("clicked");
    var id = e.target.id;
    var docId = id.split("_")[0];
    var pageId = id;
    window.location.href = 'https://s3.amazonaws.com/frontend.noteshare/document.html?q=' + docId + '&p=' + pageId;

}