

UPDATE business
SET numcheckins = counted.totalcheckins
FROM 
(
    SELECT business_id, SUM(count) as totalcheckins from check_ins group by business_id    
) as counted
WHERE business.business_id = counted.business_id



UPDATE Business
SET review_count = R.reviewCount
FROM (SELECT business_id, COUNT(*) AS reviewCount
      FROM Reviews
      GROUP BY business_id
     ) AS R
WHERE Business.business_id = R.business_id


UPDATE Business
SET reviewrating = (
    SELECT AVG(stars)
    FROM Reviews
    WHERE Reviews.business_id = Business.business_id
)