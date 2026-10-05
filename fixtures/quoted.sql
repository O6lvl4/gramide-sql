CrEaTe TaBlE "日本の表" (
  "名" TEXT,
  [value] BLOB,
  `weird``name` INTEGER
);
InSeRt InTo "日本の表" ("名", [value]) VaLuEs ('café', X'CAFE');
SeLeCt "名", [value], :parameter, ?1 FROM "日本の表";
