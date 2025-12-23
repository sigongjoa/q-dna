import React, { useState } from 'react';
import { List, ListItem, ListItemButton, ListItemIcon, ListItemText, Collapse, Checkbox } from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

// Type definition mirroring Backend Ltree logic
export interface CurriculumNode {
    id: number;
    name: string;
    path: string; // "Math.Algebra.Quadratics"
    children?: CurriculumNode[];
}

// Mock Data Structure representing ltree
const MOCK_CURRICULUM: CurriculumNode[] = [
    {
        id: 1, name: 'Mathematics', path: 'Math', children: [
            {
                id: 2, name: 'Algebra', path: 'Math.Algebra', children: [
                    { id: 3, name: 'Linear Equations', path: 'Math.Algebra.Linear' },
                    {
                        id: 4, name: 'Quadratics', path: 'Math.Algebra.Quadratics', children: [
                            { id: 5, name: 'Factoring', path: 'Math.Algebra.Quadratics.Factoring' },
                            { id: 6, name: 'Quadratic Formula', path: 'Math.Algebra.Quadratics.Formula' }
                        ]
                    }
                ]
            },
            {
                id: 7, name: 'Geometry', path: 'Math.Geometry', children: [
                    { id: 8, name: 'Triangles', path: 'Math.Geometry.Triangles' },
                    { id: 9, name: 'Circles', path: 'Math.Geometry.Circles' }
                ]
            }
        ]
    },
    {
        id: 10, name: 'Science', path: 'Science', children: [
            { id: 11, name: 'Physics', path: 'Science.Physics' },
            { id: 12, name: 'Chemistry', path: 'Science.Chemistry' }
        ]
    }
];

interface TreeNodeProps {
    node: CurriculumNode;
    selectedIds: number[];
    onToggle: (id: number) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({ node, selectedIds, onToggle }) => {
    const [open, setOpen] = useState(false);
    const hasChildren = node.children && node.children.length > 0;
    const isSelected = selectedIds.includes(node.id);

    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setOpen(!open);
    };

    const handleCheck = () => {
        onToggle(node.id);
    };

    return (
        <>
            <ListItem disablePadding sx={{ pl: 2 }}>
                <ListItemButton onClick={hasChildren ? handleClick : undefined} dense>
                    {hasChildren ? (open ? <ExpandLess /> : <ExpandMore />) : <Box sx={{ width: 24 }} />}
                    <Checkbox
                        edge="start"
                        checked={isSelected}
                        tabIndex={-1}
                        disableRipple
                        onClick={(e) => { e.stopPropagation(); handleCheck(); }}
                    />
                    <ListItemText primary={node.name} secondary={node.path} />
                </ListItemButton>
            </ListItem>
            {hasChildren && (
                <Collapse in={open} timeout="auto" unmountOnExit>
                    <List component="div" disablePadding>
                        {node.children!.map((child) => (
                            <TreeNode key={child.id} node={child} selectedIds={selectedIds} onToggle={onToggle} />
                        ))}
                    </List>
                </Collapse>
            )}
        </>
    );
};

import { Box } from '@mui/material';

export default function CurriculumTree({ onSelectionChange }: { onSelectionChange: (ids: number[]) => void }) {
    const [selected, setSelected] = useState<number[]>([]);

    const handleToggle = (id: number) => {
        const newSelected = selected.includes(id)
            ? selected.filter(sid => sid !== id)
            : [...selected, id];
        setSelected(newSelected);
        onSelectionChange(newSelected);
    };

    return (
        <Box sx={{ width: '100%', bgcolor: 'background.paper', border: '1px solid #ddd', borderRadius: 1 }}>
            <List
                component="nav"
                aria-labelledby="nested-list-subheader"
            >
                {MOCK_CURRICULUM.map(node => (
                    <TreeNode key={node.id} node={node} selectedIds={selected} onToggle={handleToggle} />
                ))}
            </List>
        </Box>
    );
}
