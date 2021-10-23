function deleteAudio(url, hashCode)
    {
        if(confirm('Are you sure that you want to delete the record?'))
        {
            var xhReq = new XMLHttpRequest();
            xhReq.open("GET", url, false);
            xhReq.send(null);
            var serverResponse = xhReq.responseText;
            // delete object from the page
            card = document.getElementById(hashCode);
            if(card != null)
            {
                card.remove();
            }
            // redirection if we are not in index
            if(location.pathname != "/")
            {
                location="/";
            }
        }
    }