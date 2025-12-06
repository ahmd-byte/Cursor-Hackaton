import imgImg62931 from "figma:asset/d8f0aa6f0feb41d115628d6cd3fc85fb3a46f412.png";

function Paragraph() {
  return <div className="absolute h-[47.961px] left-[23.98px] top-[255.88px] w-[194.568px]" data-name="Paragraph" />;
}

function Group() {
  return (
    <div className="absolute contents left-[calc(50%-0.07px)] top-[calc(50%+33.17px)] translate-x-[-50%] translate-y-[-50%]">
      <div className="absolute h-[190.407px] left-[calc(50%-0.08px)] top-[calc(50%-7.96px)] translate-x-[-50%] translate-y-[-50%] w-[179.266px]" data-name="IMG_6293 1">
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgImg62931} />
      </div>
      <div className="absolute font-['Momo_Trust_Display:Regular',sans-serif] leading-[29.673px] left-[calc(50%-0.07px)] not-italic text-[19.782px] text-center text-white top-[calc(50%+109.49px)] translate-x-[-50%] w-[278.182px]">
        <p className="mb-0">{`Bottl is now happily `}</p>
        <p>filling up your buckets!</p>
      </div>
    </div>
  );
}

function TransferPage() {
  return (
    <div className="h-[886.32px] relative shrink-0 w-full" data-name="TransferPage">
      <div className="size-full">
        <div className="content-stretch flex flex-col gap-[31.988px] h-[886.32px] items-start pb-0 pt-[23.98px] px-[23.98px] relative w-full">
          <Paragraph />
          <Group />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="absolute bg-gradient-to-b content-stretch flex flex-col from-[#83d6e2] h-[1014.31px] items-start left-0 overflow-clip to-[#2820ff] top-0 w-[369.148px]" data-name="App">
      <TransferPage />
    </div>
  );
}

export default function FintechAppOnboardingPages() {
  return (
    <div className="relative size-full" data-name="Fintech App Onboarding Pages" style={{ backgroundImage: "linear-gradient(rgb(131, 214, 226) 0%, rgb(57, 48, 243) 100%), linear-gradient(90deg, rgb(255, 255, 255) 0%, rgb(255, 255, 255) 100%)" }}>
      <App />
    </div>
  );
}