# Mobile Optimization Quick Reference Guide

## Overview
This guide provides quick reference for the mobile optimizations implemented in the client details page.

## Responsive Breakpoint
- **Breakpoint**: `md` (768px)
- **Detection**: `const screens = useBreakpoint()` from Ant Design Grid
- **Mobile Check**: `const isMobile = !screens.md`

## Key Optimization Patterns

### 1. Touch Target Sizes
**Minimum Size**: 44x44px for all interactive elements

```typescript
// Button with minimum touch target
<Button
  style={{ 
    minWidth: isMobile ? 44 : undefined, 
    minHeight: isMobile ? 44 : undefined 
  }}
>
  {isMobile ? '' : 'Label'}
</Button>
```

### 2. Font Sizes
**Mobile Font Sizes**:
- Headings: 14-18px
- Body text: 13-14px
- Metadata: 12px

```typescript
<Text style={{ fontSize: isMobile ? 14 : undefined }}>
  Content
</Text>
```

### 3. Full-Width Cards on Mobile
**Pattern**: Negative margins to extend edge-to-edge

```typescript
<Card
  bordered={!isMobile}
  style={{ 
    marginLeft: isMobile ? -8 : 0,
    marginRight: isMobile ? -8 : 0,
    borderRadius: isMobile ? 0 : undefined
  }}
>
  Content
</Card>
```

### 4. Responsive Spacing
**Pattern**: Reduced spacing on mobile

```typescript
<Space 
  size={isMobile ? 'small' : 'middle'}
  style={{ marginBottom: isMobile ? 12 : 16 }}
>
  Content
</Space>
```

### 5. Conditional Text Display
**Pattern**: Shorter labels on mobile

```typescript
{isMobile ? '上传' : '重新上传'}
```

### 6. Word Breaking
**Pattern**: Prevent layout breaking with long text

```typescript
<Text 
  style={{ 
    wordBreak: 'break-word',
    maxWidth: isMobile ? '200px' : undefined
  }}
  ellipsis={isMobile ? { tooltip: fullText } : false}
>
  {text}
</Text>
```

### 7. Icon-Only Buttons
**Pattern**: Show only icons on mobile to save space

```typescript
<Button
  icon={<EyeOutlined />}
  style={{ minWidth: isMobile ? 44 : undefined }}
>
  {isMobile ? '' : '预览'}
</Button>
```

### 8. Responsive Component Sizes
**Pattern**: Adjust component sizes for mobile

```typescript
<Tabs
  size={isMobile ? 'middle' : 'large'}
/>

<Descriptions
  size={isMobile ? 'small' : 'default'}
/>
```

## Component-Specific Optimizations

### CustomerDetail.tsx
```typescript
// Shortened tab labels
label: isMobile ? (
  <span style={{ fontSize: 14 }}>
    <UserOutlined /> 基本
  </span>
) : (
  <span>
    <UserOutlined /> 基本信息
  </span>
)

// Icon-only back button
<Button icon={<ArrowLeftOutlined />}>
  {isMobile ? '' : '返回'}
</Button>

// Smaller title
<Title level={isMobile ? 4 : 2}>
  客户详情
</Title>
```

### BasicInfoTab.tsx
```typescript
<Descriptions
  column={{ xs: 1, sm: 2, md: 2 }}
  size={isMobile ? 'small' : 'default'}
  labelStyle={{ 
    fontSize: isMobile ? 14 : undefined,
    padding: isMobile ? '8px 12px' : undefined
  }}
  contentStyle={{
    fontSize: isMobile ? 14 : undefined,
    padding: isMobile ? '8px 12px' : undefined,
    wordBreak: 'break-word'
  }}
/>
```

### DocumentUploadTab.tsx
```typescript
// Card styling
<Card
  style={{ 
    marginBottom: isMobile ? 12 : 16,
    marginLeft: isMobile ? -8 : 0,
    marginRight: isMobile ? -8 : 0,
    borderRadius: isMobile ? 0 : undefined
  }}
/>

// Upload dragger
<Dragger>
  <p className="ant-upload-text" style={{ fontSize: isMobile ? 14 : undefined }}>
    {isMobile ? '点击或拖拽上传' : '点击或拖拽文件到此区域上传'}
  </p>
</Dragger>

// Full-width upload button
<Button
  type="primary"
  size={isMobile ? 'middle' : 'large'}
  style={{ 
    minWidth: isMobile ? '100%' : undefined,
    minHeight: isMobile ? 44 : undefined
  }}
>
  开始上传
</Button>

// Progress bar
<Progress
  strokeWidth={isMobile ? 12 : undefined}
/>
```

### ReviewHistoryTab.tsx
```typescript
<Timeline mode={isMobile ? 'left' : undefined}>
  <Timeline.Item>
    <Text strong style={{ fontSize: isMobile ? 14 : undefined }}>
      {title}
    </Text>
    <Text style={{ 
      fontSize: isMobile ? 13 : undefined,
      wordBreak: 'break-word'
    }}>
      {content}
    </Text>
  </Timeline.Item>
</Timeline>
```

## Testing Checklist

### Visual Testing
- [ ] Test on iPhone SE (320px) - smallest screen
- [ ] Test on iPhone 8 (375px) - standard mobile
- [ ] Test on iPhone 12 Pro (390px) - modern mobile
- [ ] Test on iPhone 12 Pro Max (428px) - large mobile
- [ ] Test on iPad (768px) - tablet breakpoint

### Functional Testing
- [ ] All buttons are tappable (44x44px minimum)
- [ ] Text is readable (12px minimum)
- [ ] No horizontal scrolling
- [ ] No layout breaking with long text
- [ ] Upload interface works correctly
- [ ] All tabs are accessible
- [ ] Action buttons work correctly

### Accessibility Testing
- [ ] Touch targets meet WCAG 2.1 Level AAA (44x44px)
- [ ] Text contrast is sufficient
- [ ] Font sizes are readable
- [ ] Interactive elements are clearly identifiable

## Common Pitfalls to Avoid

1. **Don't forget to import Grid**: `import { Grid } from 'antd'`
2. **Don't use fixed widths**: Use percentages or flex layouts
3. **Don't forget word-break**: Long text can break layouts
4. **Don't make touch targets too small**: Minimum 44x44px
5. **Don't use tiny fonts**: Minimum 12px for readability
6. **Don't forget to test on real devices**: Emulation is good but not perfect

## Performance Tips

1. **Use CSS for responsive design**: Avoid JavaScript-based resizing
2. **Minimize re-renders**: Use useMemo/useCallback where appropriate
3. **Optimize images**: Use responsive images with srcset
4. **Lazy load content**: Load content as needed
5. **Use virtual scrolling**: For long lists

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Safari 14+
- ✅ Firefox 88+
- ✅ iOS Safari 14+
- ✅ Chrome Mobile 90+

## Resources

- [Ant Design Grid Documentation](https://ant.design/components/grid)
- [WCAG 2.1 Touch Target Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/target-size.html)
- [Mobile-First Design Principles](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Responsive/Mobile_first)

## Maintenance

When adding new features:
1. Always check `isMobile` for responsive behavior
2. Test on multiple screen sizes
3. Ensure touch targets are at least 44x44px
4. Use appropriate font sizes
5. Handle long text with word-break
6. Follow the patterns in this guide

