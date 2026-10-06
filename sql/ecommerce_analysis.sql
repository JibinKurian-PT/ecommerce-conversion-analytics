#How many unique visitors reached each stage of the shopping funnel?
USE retail_analytics;

SELECT
    COUNT(DISTINCT visitorid) AS total_visitors,

    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'addtocart'
        THEN visitorid
    END) AS cart_users,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers

FROM fact_events;

#What percentage of visitors moved from one funnel stage to the next?
USE retail_analytics;

SELECT
    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'addtocart'
        THEN visitorid
    END) AS cart_users,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN event = 'addtocart'
            THEN visitorid
        END)
        /
        COUNT(DISTINCT CASE
            WHEN event = 'view'
            THEN visitorid
        END) * 100,
        2
    ) AS view_to_cart_pct,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN event = 'transaction'
            THEN visitorid
        END)
        /
        COUNT(DISTINCT CASE
            WHEN event = 'addtocart'
            THEN visitorid
        END) * 100,
        2
    ) AS cart_to_purchase_pct,

    ROUND(
        COUNT(DISTINCT CASE
            WHEN event = 'transaction'
            THEN visitorid
        END)
        /
        COUNT(DISTINCT CASE
            WHEN event = 'view'
            THEN visitorid
        END) * 100,
        2
    ) AS view_to_purchase_pct

FROM fact_events;

#Where is the biggest funnel drop-off?
WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END) AS viewers,
        COUNT(DISTINCT CASE WHEN event = 'addtocart' THEN visitorid END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS purchasers
    FROM fact_events
)

SELECT
    viewers,
    cart_users,
    purchasers,

    ROUND(
        (viewers - cart_users) / viewers * 100,
        2
    ) AS view_to_cart_dropoff_pct,

    ROUND(
        (cart_users - purchasers) / cart_users * 100,
        2
    ) AS cart_to_purchase_dropoff_pct

FROM funnel;

#Phase 2 — Sequential Funnel Behavior
#Q4. How many visitors actually followed View → Cart → Purchase?
WITH visitor_journey AS (

    SELECT
        visitorid,

        MIN(CASE
            WHEN event = 'view'
            THEN event_timestamp
        END) AS first_view,

        MIN(CASE
            WHEN event = 'addtocart'
            THEN event_timestamp
        END) AS first_cart,

        MIN(CASE
            WHEN event = 'transaction'
            THEN event_timestamp
        END) AS first_transaction

    FROM fact_events
    GROUP BY visitorid
)

SELECT
    COUNT(*) AS total_visitors,

    SUM(
        CASE
            WHEN first_view IS NOT NULL
            AND first_cart IS NOT NULL
            AND first_transaction IS NOT NULL
            AND first_view < first_cart
            AND first_cart < first_transaction
            THEN 1
            ELSE 0
        END
    ) AS completed_funnel_visitors,

    ROUND(
        SUM(
            CASE
                WHEN first_view IS NOT NULL
                AND first_cart IS NOT NULL
                AND first_transaction IS NOT NULL
                AND first_view < first_cart
                AND first_cart < first_transaction
                THEN 1
                ELSE 0
            END
        )
        /
        COUNT(*)
        * 100,
        2
    ) AS complete_funnel_pct

FROM visitor_journey;

#Q5. How many cart users have no recorded purchase after their first cart?
WITH visitor_journey AS (

    SELECT
        visitorid,

        MIN(CASE
            WHEN event = 'addtocart'
            THEN event_timestamp
        END) AS first_cart,

        MIN(CASE
            WHEN event = 'transaction'
            THEN event_timestamp
        END) AS first_transaction

    FROM fact_events
    GROUP BY visitorid
)

SELECT
    COUNT(*) AS cart_users_without_recorded_purchase

FROM visitor_journey

WHERE first_cart IS NOT NULL
AND (
    first_transaction IS NULL
    OR first_transaction < first_cart
);

#Q6. How many purchases occurred without a recorded prior cart?
WITH visitor_journey AS (

    SELECT
        visitorid,

        MIN(CASE
            WHEN event = 'addtocart'
            THEN event_timestamp
        END) AS first_cart,

        MIN(CASE
            WHEN event = 'transaction'
            THEN event_timestamp
        END) AS first_transaction

    FROM fact_events
    GROUP BY visitorid
)

SELECT
    COUNT(*) AS purchases_without_prior_recorded_cart

FROM visitor_journey

WHERE first_transaction IS NOT NULL
AND (
    first_cart IS NULL
    OR first_transaction < first_cart
);

#Phase 3 — Customer Behavior
#Q7. How many events does the average visitor generate?
SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT visitorid) AS unique_visitors,

    ROUND(
        COUNT(*) / COUNT(DISTINCT visitorid),
        2
    ) AS avg_events_per_visitor

FROM fact_events;

#Q8. How many visitors are one-event vs repeat visitors?
WITH visitor_activity AS (

    SELECT
        visitorid,
        COUNT(*) AS event_count
    FROM fact_events
    GROUP BY visitorid
)

SELECT
    CASE
        WHEN event_count = 1 THEN 'One Event'
        ELSE 'Multiple Events'
    END AS visitor_type,

    COUNT(*) AS visitors,

    ROUND(
        COUNT(*) /
        (SELECT COUNT(*) FROM visitor_activity) * 100,
        2
    ) AS visitor_pct

FROM visitor_activity

GROUP BY
    CASE
        WHEN event_count = 1 THEN 'One Event'
        ELSE 'Multiple Events'
    END;
    
    #Q9. Which visitors show the highest activity?
    SELECT
    visitorid,
    COUNT(*) AS total_events,

    SUM(event = 'view') AS views,
    SUM(event = 'addtocart') AS add_to_carts,
    SUM(event = 'transaction') AS transactions

FROM fact_events

GROUP BY visitorid

ORDER BY total_events DESC

LIMIT 20;

#Phase 4 — Time Analysis
#Q10. How does customer activity change by day?
SELECT
    DATE(
        FROM_UNIXTIME(event_timestamp / 1000)
    ) AS event_date,

    COUNT(*) AS total_events,

    COUNT(DISTINCT visitorid) AS unique_visitors

FROM fact_events

GROUP BY event_date

ORDER BY event_date;

#Q11. How many views, carts, and transactions happen each day?
SELECT
    DATE(
        FROM_UNIXTIME(event_timestamp / 1000)
    ) AS event_date,

    SUM(event = 'view') AS views,

    SUM(event = 'addtocart') AS add_to_carts,

    SUM(event = 'transaction') AS transactions

FROM fact_events

GROUP BY event_date

ORDER BY event_date;

#Q12. What is the daily visitor-to-purchase conversion rate?
WITH daily_funnel AS (

    SELECT
        DATE(
            FROM_UNIXTIME(event_timestamp / 1000)
        ) AS event_date,

        COUNT(DISTINCT CASE
            WHEN event = 'view'
            THEN visitorid
        END) AS viewers,

        COUNT(DISTINCT CASE
            WHEN event = 'transaction'
            THEN visitorid
        END) AS purchasers

    FROM fact_events

    GROUP BY event_date
)

SELECT
    event_date,
    viewers,
    purchasers,

    ROUND(
        purchasers / NULLIF(viewers, 0) * 100,
        2
    ) AS view_to_purchase_pct

FROM daily_funnel

ORDER BY event_date;

#Phase 5 — Category Analysis
#Q13. Which categories receive the most customer activity?
SELECT
    categoryid,

    COUNT(*) AS total_events,

    COUNT(DISTINCT visitorid) AS unique_visitors,

    SUM(event = 'view') AS views,

    SUM(event = 'addtocart') AS add_to_carts,

    SUM(event = 'transaction') AS transactions

FROM fact_events

WHERE categoryid IS NOT NULL

GROUP BY categoryid

ORDER BY total_events DESC

LIMIT 20;

#Q14. Which categories have the highest observed conversion?
SELECT
    categoryid,

    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'addtocart'
        THEN visitorid
    END) AS cart_users,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
        /
        NULLIF(
            COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END),
            0
        )
        * 100,
        2
    ) AS view_to_purchase_pct

FROM fact_events

WHERE categoryid IS NOT NULL

GROUP BY categoryid

HAVING viewers >= 50

ORDER BY view_to_purchase_pct DESC

LIMIT 20;

#Q15. Which categories get many views but relatively few purchases?
SELECT
    categoryid,

    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
        /
        NULLIF(
            COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END),
            0
        )
        * 100,
        2
    ) AS view_to_purchase_pct

FROM fact_events

WHERE categoryid IS NOT NULL

GROUP BY categoryid

HAVING viewers >= 100

ORDER BY view_to_purchase_pct ASC

LIMIT 20;

#Phase 6 — Availability Analysis
#Q16. How much activity occurs under each availability state?
SELECT
    CASE
        WHEN available = 1 THEN 'Available'
        WHEN available = 0 THEN 'Unavailable'
        ELSE 'Unknown / Not Matched'
    END AS availability_status,

    COUNT(*) AS total_events,

    COUNT(DISTINCT visitorid) AS unique_visitors

FROM fact_events

GROUP BY
    CASE
        WHEN available = 1 THEN 'Available'
        WHEN available = 0 THEN 'Unavailable'
        ELSE 'Unknown / Not Matched'
    END

ORDER BY total_events DESC;

#Q17. Is availability associated with observed purchase conversion?
SELECT
    CASE
        WHEN available = 1 THEN 'Available'
        WHEN available = 0 THEN 'Unavailable'
        ELSE 'Unknown / Not Matched'
    END AS availability_status,

    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
        /
        NULLIF(
            COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END),
            0
        )
        * 100,
        2
    ) AS view_to_purchase_pct

FROM fact_events

GROUP BY
    CASE
        WHEN available = 1 THEN 'Available'
        WHEN available = 0 THEN 'Unavailable'
        ELSE 'Unknown / Not Matched'
    END;
    
    #Phase 7 — Product Analysis
    #Q18. Which products receive the most views?
    SELECT
    itemid,

    COUNT(DISTINCT visitorid) AS unique_viewers,

    COUNT(*) AS view_events

FROM fact_events

WHERE event = 'view'

GROUP BY itemid

ORDER BY unique_viewers DESC

LIMIT 20;

#Q19. Which products have the strongest observed view-to-purchase conversion?
SELECT
    itemid,

    COUNT(DISTINCT CASE
        WHEN event = 'view'
        THEN visitorid
    END) AS viewers,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
        /
        NULLIF(
            COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END),
            0
        )
        * 100,
        2
    ) AS view_to_purchase_pct

FROM fact_events

GROUP BY itemid

HAVING viewers >= 50

ORDER BY view_to_purchase_pct DESC

LIMIT 20;

#Q20. Which products get many views but no recorded purchase?
SELECT
    itemid,

    COUNT(DISTINCT visitorid) AS unique_viewers,

    COUNT(*) AS view_events

FROM fact_events

WHERE event = 'view'

GROUP BY itemid

HAVING COUNT(DISTINCT visitorid) >= 100

AND itemid NOT IN (
    SELECT DISTINCT itemid
    FROM fact_events
    WHERE event = 'transaction'
)

ORDER BY unique_viewers DESC

LIMIT 20;

#Q21. Which products have strong cart activity but relatively fewer purchases?
SELECT
    itemid,

    COUNT(DISTINCT CASE
        WHEN event = 'addtocart'
        THEN visitorid
    END) AS cart_users,

    COUNT(DISTINCT CASE
        WHEN event = 'transaction'
        THEN visitorid
    END) AS purchasers,

    ROUND(
        COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
        /
        NULLIF(
            COUNT(DISTINCT CASE WHEN event = 'addtocart' THEN visitorid END),
            0
        )
        * 100,
        2
    ) AS cart_to_purchase_pct

FROM fact_events

GROUP BY itemid

HAVING cart_users >= 20

ORDER BY cart_to_purchase_pct ASC

LIMIT 20;

#Phase 8 — Data Quality & Tracking
#Q22. How many events have no historical category match?
SELECT
    CASE
        WHEN categoryid IS NULL
        THEN 'No Category Match'
        ELSE 'Category Matched'
    END AS category_status,

    COUNT(*) AS events,

    ROUND(
        COUNT(*) /
        (SELECT COUNT(*) FROM fact_events)
        * 100,
        2
    ) AS event_pct

FROM fact_events

GROUP BY
    CASE
        WHEN categoryid IS NULL
        THEN 'No Category Match'
        ELSE 'Category Matched'
    END;
    
    #Q23. How many events have no historical availability match?
    SELECT
    CASE
        WHEN available IS NULL
        THEN 'No Availability Match'
        ELSE 'Availability Matched'
    END AS availability_status,

    COUNT(*) AS events,

    ROUND(
        COUNT(*) /
        (SELECT COUNT(*) FROM fact_events)
        * 100,
        2
    ) AS event_pct

FROM fact_events

GROUP BY
    CASE
        WHEN available IS NULL
        THEN 'No Availability Match'
        ELSE 'Availability Matched'
    END;