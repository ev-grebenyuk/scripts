#stands="demo-data"
topics="config offset status"
bs="sh06-kafka01:9092"
rf=2
for stand in $stands; do
  for t in $topics; do
    ./kafka-topics.sh --bootstrap-server ${bs} --delete --topic "${stand}_cp-kafka-connect-$t";
      case $t in
        "config")
          prt=1
          ;;
        "offset")
          prt=25
          ;;
        "status")
          prt=5
          ;;
      esac
    ./kafka-topics.sh --bootstrap-server ${bs} --create --topic "${stand}_cp-kafka-connect-$t" --partitions ${prt} --replication-factor ${rf} --config cleanup.policy=compact;
  done
done
