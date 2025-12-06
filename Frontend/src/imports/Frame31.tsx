import svgPaths from "./svg-kxo81zw4r5";

function Group() {
  return (
    <div className="h-[122px] relative shrink-0 w-[114.146px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 115 122">
        <g id="Group 4">
          <ellipse cx="57.0733" cy="61" fill="var(--fill-0, white)" id="Ellipse 7" rx="42.4395" ry="49.1816" transform="rotate(20.6796 57.0733 61)" />
          <ellipse cx="63.5792" cy="60.3696" fill="var(--fill-0, #111922)" id="Ellipse 8" rx="34.8682" ry="38.2075" transform="rotate(34.91 63.5792 60.3696)" />
          <path d={svgPaths.p117f3900} fill="var(--fill-0, #FEFF09)" id="Vector 1" />
          <path d={svgPaths.p1d0bf700} fill="var(--fill-0, #FEFF09)" id="Vector 2" stroke="var(--stroke-0, #FEFF09)" />
        </g>
      </svg>
    </div>
  );
}

function Group1() {
  return (
    <div className="h-[120.321px] relative w-[112.576px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 113 121">
        <g id="Group 5">
          <ellipse cx="56.2878" cy="60.1607" fill="var(--fill-0, white)" id="Ellipse 7" rx="41.8555" ry="48.5048" transform="rotate(20.6796 56.2878 60.1607)" />
          <ellipse cx="62.7042" cy="59.5391" fill="var(--fill-0, #111922)" id="Ellipse 8" rx="34.3883" ry="37.6817" transform="rotate(34.91 62.7042 59.5391)" />
          <path d={svgPaths.p2feb9600} fill="var(--fill-0, #FEFF09)" id="Vector 1" />
          <path d={svgPaths.p62f4e00} fill="var(--fill-0, #FEFF09)" id="Vector 2" stroke="var(--stroke-0, #FEFF09)" />
        </g>
      </svg>
    </div>
  );
}

export default function Frame() {
  return (
    <div className="content-stretch flex items-center justify-between relative size-full">
      <Group />
      <div className="flex items-center justify-center relative shrink-0">
        <div className="flex-none rotate-[180deg] scale-y-[-100%]">
          <Group1 />
        </div>
      </div>
    </div>
  );
}