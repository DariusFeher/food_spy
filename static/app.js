var isHidden = [true, true];
function toggle(id) {
    var last_letter = id.charAt(id.length - 1);
    if (last_letter == "1") {
        toggle_field(last_letter);
    } else {
        toggle_field(last_letter);
    }
}

function toggle_field(fieldNo) {
    if(!isHidden[fieldNo - 1]) {
        el1 = document.getElementById("id_password" + fieldNo);
        el2 = document.getElementById("id_new_password" + fieldNo);
        if (el1) {
            el1.setAttribute("type", "password");
        } else {
            el2.setAttribute("type", "password");
        }
        document.getElementById("eye" + fieldNo).className = "fa fa-eye-slash";
        isHidden[fieldNo - 1] = true;
    } else {
        el1 = document.getElementById("id_password" + fieldNo);
        el2 = document.getElementById("id_new_password" + fieldNo);
        if (el1) {
            el1.setAttribute("type", "text");
        } else {
            el2.setAttribute("type", "text");
        }
        document.getElementById("eye" + fieldNo).className = "fa fa-eye";
        isHidden[fieldNo - 1] = false;
    }
}


function showSuccessMessage(msg) {
    M.toast({html: '<h5><i class="small material-icons">check_circle</i>  ' + msg + '</h5>', classes: 'green', displayLength: '4000'});
};
function showErrorMessage(msg) {
    M.toast({html: '<h5><i class="small material-icons">report_problem</i>  ' + msg + '</h5>', classes: 'red', displayLength: '4000'});
};
        