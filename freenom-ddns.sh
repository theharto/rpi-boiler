#!/bin/bash
 
# settings
# Login information of freenom.com
freenom_email="thedavidhart@gmail.com"
freenom_passwd="freenom5511"
# Open DNS management page in your browser.
# URL vs settings:
#   https://my.freenom.com/clientarea.php?managedns={freenom_domain_name}&domainid={freenom_domain_id}
freenom_domain_name="homefire.cf"
freenom_domain_id="1037135893"
cookie_file="./freenom-ddns-cookie.tmp"
 
# main
# get current ip address
current_ip="$(curl -s "https://api.ipify.org/")"
 
if [ "${current_ip}" == "" ]; then
    echo "Could not get current IP address." 1>&2
    exit 1
fi

echo "Internet ip = $current_ip"

rm $cookie_file

#login page
login_page=$(curl -k -v -L -c "${cookie_file}" "https://my.freenom.com/clientarea.php" 2>&1)
echo "login page $login_page"


#<input type="hidden" name="token" value="9b82d6b579a101af9f14edb0f822f73c5643e42e" />


# login

login_result=$(curl -k -v -L -b "${cookie_file}" "https://my.freenom.com/dologin.php")
#login_result=$(curl -k -v -L -b "${cookie_file}" -F "username=${freenom_email}" -F "password=${freenom_passwd}" "https://my.freenom.com/dologin.php" 2>&1)
#login_result=$(curl -k -v -L -b "${cookie_file}" -F "username=${freenom_email}" -F "password=${freenom_passwd}" "https://my.freenom.com/dologin.php" 2>&1)

echo "-- loginResult --"
echo $login_result
exit 1

echo "login result $loginResult"

exit 1;

if [ "$(echo -e "${loginResult}" | grep "/clientarea.php?incorrect=true")" != "" ]; then
    echo "Login failed." 1>&2
    exit 1
fi

# update
updateResult=$(curl --compressed -k -L -b "${cookie_file}" \
    -F "dnsaction=modify" -F "records[0][line]=" -F "records[0][type]=A" -F "records[0][name]=" -F "records[0][ttl]=14440" -F "records[0][value]=${current_ip}" \
    "https://my.freenom.com/clientarea.php?managedns=${freenom_domain_name}&domainid=${freenom_domain_id}" 2>&1)

echo "update result $updateResult"


if [ "$(echo -e "$updateResult" | grep "<li class=\"dnssuccess\">")" == "" ]; then
    echo "Update failed." 1>&2
    exit 1
fi

# logout
curl --compressed -k -b "${cookie_file}" "https://my.freenom.com/logout.php" > /dev/null 2>&1

# clean up
#rm -f ${cookie_file}

exit 0
