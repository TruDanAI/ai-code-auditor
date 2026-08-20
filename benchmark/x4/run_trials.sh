#!/bin/bash
# P-X4 Giai doan 2: chay trial-02 va trial-03 cho ca hai snapshot.
# CAU HINH PHAI GIONG HET trial-01 - ke ca --max-budget-usd 0.80. Nang tran giua
# chung = trial chay tren hai cau hinh khac nhau = so sanh hong.
#
# KHONG SUA FILE NAY TRONG LUC NO DANG CHAY: bash doc script theo byte offset,
# ghi de giua chung lam no nhay vao giua file moi va vo cu phap (da dinh 1 lan).
X4="C:/Users/Pc/AppData/Local/Temp/claude/c--Users-Pc-Desktop-Build-CV/61ab3470-28cf-49a8-ac6b-adec2243a2be/scratchpad/x4"
BUDGET_MAX=45.00
SCHEMA="$(cat "$X4/schema.json")"

for trial in trial-02 trial-03; do
  mkdir -p "$X4/raw/$trial"
  echo "=========== $trial ==========="
  for id in $(tr -d '\r' < "$X4/item_ids.txt"); do
    for snap in clean spiked; do
      out="$X4/raw/$trial/${id}__${snap}.json"
      [ -s "$out" ] && { echo "SKIP $trial/$id/$snap"; continue; }

      prompt_file="$X4/prompts/${id}.txt"
      [ -f "$prompt_file" ] || { echo "FATAL: thieu $prompt_file"; exit 1; }

      spent=$(python "$X4/spend.py")
      stop=$(python -c "print(1 if $spent >= $BUDGET_MAX else 0)")
      [ "$stop" = "1" ] && { echo "STOP: cham tran \$$BUDGET_MAX (da tieu \$$spent)"; exit 2; }

      ( cd "$X4/$snap" && claude -p "$(cat "$prompt_file")" \
          --model sonnet \
          --output-format json \
          --json-schema "$SCHEMA" \
          --allowedTools "Read Grep Glob" \
          --disallowedTools "Edit Write Bash WebFetch WebSearch" \
          --max-budget-usd 0.80 \
          --disable-slash-commands \
          --no-session-persistence ) > "$out" 2>"$X4/raw/$trial/${id}__${snap}.err"

      if [ ! -s "$out" ]; then
        echo "LOI $trial/$id/$snap -> output rong. stderr: $(head -c 200 "$X4/raw/$trial/${id}__${snap}.err")"
      else
        echo "$trial/$id/$snap  (cong don \$$(python "$X4/spend.py"))"
      fi
    done
  done
done
echo "XONG CA HAI TRIAL. Tong \$$(python "$X4/spend.py")"
