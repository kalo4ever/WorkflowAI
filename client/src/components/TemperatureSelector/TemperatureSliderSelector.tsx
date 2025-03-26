import { SliderWithInput } from '../ui/SliderWithInput';

// Some models don't support values outside of [0, 1]
// Later we can add a check for the model type and set the max value accordingly
const MAX_TEMPERATURE = 1;

type TemperatureSliderSelectorProps = {
  temperature: number;
  setTemperature: (value: number) => void;
};

export function TemperatureSliderSelector(props: TemperatureSliderSelectorProps) {
  const { temperature, setTemperature } = props;

  return (
    <div className='w-full'>
      <SliderWithInput min={0} max={MAX_TEMPERATURE} step={0.1} value={temperature} onChange={setTemperature} />
    </div>
  );
}
