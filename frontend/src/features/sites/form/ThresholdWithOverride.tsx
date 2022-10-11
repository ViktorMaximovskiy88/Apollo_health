import { Checkbox, Form, Slider } from 'antd';

const formatter = (value?: number) => {
  if (value == null) return;
  const displayedValue = Math.round(value * 100); // fix floating point math bugs
  return `${displayedValue}%`;
};

interface ThresholdWithOverrideProps {
  overrideName: string;
  overrideLabel: string;
  thresholdName: string;
  thresholdLabel: string;
}
export function ThresholdWithOverride({
  overrideName,
  overrideLabel,
  thresholdName,
  thresholdLabel,
}: ThresholdWithOverrideProps) {
  const form = Form.useFormInstance();
  const thresholdOverride = Form.useWatch(overrideName, form);
  return (
    <>
      <Form.Item name={overrideName} label={overrideLabel} valuePropName="checked">
        <Checkbox />
      </Form.Item>
      {thresholdOverride ? (
        <Form.Item name={thresholdName} label={thresholdLabel}>
          <Slider
            min={0}
            max={1}
            step={0.01}
            tooltip={{
              open: true,
              placement: 'left',
              formatter,
              getPopupContainer: (triggerNode) => triggerNode.parentElement ?? triggerNode, // fixes tooltip to be inline with element -- https://github.com/ant-design/ant-design/issues/25117#issuecomment-873747921
            }}
          />
        </Form.Item>
      ) : null}
    </>
  );
}
