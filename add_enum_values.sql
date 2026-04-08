-- Add new status values to the marks table ENUM

ALTER TABLE marks 
MODIFY COLUMN status ENUM(
    'ENTERED',
    'MODERATED', 
    'FINALIZED',
    'Assigned',
    'Draft',
    'Approved'
) DEFAULT NULL;

-- Verify the change
SELECT COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'examease' 
AND TABLE_NAME = 'marks' 
AND COLUMN_NAME = 'status';
