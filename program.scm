(begin
    (define circle-area (-> r (mul pi (mul r r))))
    (define lst (list 5 10))
    (circle-area (add 5 (sub 10 (fst lst))))
)