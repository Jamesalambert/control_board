if [ "$1" = "" ] #need spaces next to [] and ""
	then
	echo "-- you need to type in a message please"
	exit 1
fi

git add --all
echo "-- commiting changes"
git commit -m "$1"
echo "-- pushing changes"
git push -u origin master
echo "-- finished"